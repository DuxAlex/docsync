import os
import base64
import requests
import google.generativeai as genai
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

# --- Configurações e Chaves ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Configura o modelo Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    print(f"❌ Erro ao configurar o Gemini: {e}")
    model = None

# --- Funções de Interação com o GitHub ---

def obter_dono_e_repositorio(repo_url):
    if not repo_url: return None, None
    try:
        parts = repo_url.strip().rstrip("/").replace(".git", "").split("/")
        return parts[-2], parts[-1]
    except IndexError:
        return None, None

def listar_branches(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return [branch['name'] for branch in res.json()], None
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code
        if status_code == 404: return [], "Repositório não encontrado. Verifique a URL."
        if status_code == 401: return [], "Acesso não autorizado. Verifique seu GITHUB_TOKEN."
        return [], f"Erro na API do GitHub ({status_code})."
    except requests.exceptions.RequestException as e:
        return [], f"Erro de conexão: {e}"

def obter_commits_da_branch(owner, repo, branch_name, limit=5):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {'sha': branch_name, 'per_page': limit}
    try:
        res = requests.get(url, headers=HEADERS, params=params, timeout=10)
        res.raise_for_status()
        return [commit['commit']['message'] for commit in res.json()]
    except requests.exceptions.RequestException:
        return []

def obter_arquivos_repo(owner, repo, branch):
    """Busca o conteúdo de arquivos relevantes do repositório."""
    print(f"🌳 Buscando árvore de arquivos da branch '{branch}'...")
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    res = requests.get(tree_url, headers=HEADERS)
    if res.status_code != 200:
        print("   └── Falha ao obter árvore de arquivos.")
        return ""

    tree = res.json().get("tree", [])
    arquivos_texto = ""
    extensoes_relevantes = ['.js', '.py', '.html', '.css', '.java', 'go', 'rb', 'php', 'ts']
    arquivos_filtrados = [f for f in tree if any(f['path'].endswith(ext) for ext in extensoes_relevantes) and f['type'] == 'blob']
    
    print(f"   └── Encontrados {len(arquivos_filtrados)} arquivos relevantes. Analisando até 10.")

    for file_data in arquivos_filtrados[:10]:
        blob_url = file_data['url']
        blob_res = requests.get(blob_url, headers=HEADERS)
        if blob_res.status_code == 200:
            content_b64 = blob_res.json().get('content', '')
            try:
                content_decodificado = base64.b64decode(content_b64).decode('utf-8')
                arquivos_texto += f"\n\n--- INÍCIO DO ARQUIVO: {file_data['path']} ---\n"
                arquivos_texto += content_decodificado
                arquivos_texto += f"\n--- FIM DO ARQUIVO: {file_data['path']} ---\n"
            except Exception:
                continue
    
    return arquivos_texto

# --- Configuração do Flask ---
app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    if not model:
        return jsonify({"error": "Modelo de IA não inicializado."}), 500

    data = request.json
    repo_url = data.get("repo_url")
    if not repo_url:
        return jsonify({"error": "URL do repositório é obrigatória."}), 400

    owner, repo = obter_dono_e_repositorio(repo_url)
    if not owner or not repo:
        return jsonify({"error": "URL do repositório inválida."}), 400

    branches, error = listar_branches(owner, repo)
    if error: return jsonify({"error": error}), 400
    if not branches: return jsonify({"error": "Nenhuma branch encontrada."}), 404

    branch_principal = branches[0]
    print(f"🌿 Analisando a branch principal: {branch_principal}")

    historico_de_commits = "\n".join(obter_commits_da_branch(owner, repo, branch_principal))
    codigo_dos_arquivos = obter_arquivos_repo(owner, repo, branch_principal)

    if not historico_de_commits and not codigo_dos_arquivos:
        return jsonify({"error": "Não foi possível encontrar commits ou arquivos de código para analisar."}), 404

    # PROMPT ATUALIZADO PARA SOLICITAR SNIPPETS DE CÓDIGO
    prompt = f"""
    Você é um engenheiro de software sênior e um especialista em análise de código estático.
    Sua tarefa é analisar um repositório, gerar um README.md e identificar potenciais bugs ou melhorias.

    **DADOS DO REPOSITÓRIO:**
    1. Histórico de Commits Recentes: {historico_de_commits}
    2. Conteúdo de Arquivos Relevantes: {codigo_dos_arquivos}

    **TAREFA:**
    Gere uma resposta JSON com DUAS chaves: "readme" e "bugs".

    1.  **"readme"**: Uma string contendo um README.md completo em formato Markdown.
    2.  **"bugs"**: Um ARRAY de objetos JSON. Cada objeto deve ter as chaves: "title", "filepath", "severity" ('Baixa', 'Média', 'Alta'), "type" ('Bug', 'Melhoria'), "problem" (descrição do problema), "suggestion" (sugestão de correção), "code_before" (o trecho de código exato com o problema) e "code_after" (o trecho de código exato com a sugestão de correção).

    Responda APENAS com o objeto JSON.
    """

    try:
        print("🤖 Enviando dados para análise completa no Gemini...")
        resposta = model.generate_content(prompt)
        cleaned_response = resposta.text.strip().replace("```json", "").replace("```", "").strip()
        analysis_json = json.loads(cleaned_response)
        print("✅ Análise completa recebida.")
        return jsonify(analysis_json)
    except Exception as e:
        print(f"❌ Erro ao processar resposta da IA: {e}\nResposta recebida: {resposta.text}")
        return jsonify({"error": "Erro ao gerar análise. A resposta da IA não estava no formato esperado."}), 500

@app.route("/analyze-complexity", methods=["POST"])
def analyze_complexity():
    if not model:
        return jsonify({"error": "O modelo de IA não foi inicializado."}), 500

    data = request.json
    code_snippet = data.get("code")

    if not code_snippet or not code_snippet.strip():
        return jsonify({"error": "Nenhum trecho de código foi fornecido."}), 400

    prompt = f"""
    Você é um engenheiro de software sênior, especialista em design de algoritmos e otimização de performance.
    Sua tarefa é analisar o seguinte trecho de código e fornecer uma análise de complexidade detalhada.

    Código para Análise:
    ```
    {code_snippet}
    ```

    Por favor, forneça sua análise estritamente no seguinte formato JSON, com as chaves "overall_complexity", "bottlenecks" e "suggestions".
    JSON de saída:
    """

    try:
        resposta = model.generate_content(prompt)
        cleaned_response = resposta.text.strip().replace("```json", "").replace("```", "").strip()
        analysis_json = json.loads(cleaned_response)
        return jsonify(analysis_json)
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar análise com o modelo de IA: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
