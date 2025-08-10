import os
import base64
import requests
import google.generativeai as genai
import json
import re
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

# --- Configurações e Chaves ---
SERVER_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    print(f"❌ Erro ao configurar o Gemini: {e}")
    model = None

# --- Funções Auxiliares ---

def get_auth_headers(user_token=None):
    """Cria os cabeçalhos de autenticação, priorizando o token do utilizador."""
    token = user_token or SERVER_GITHUB_TOKEN
    if not token:
        return None
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def obter_dono_e_repositorio(repo_url):
    if not repo_url: return None, None
    try:
        parts = repo_url.strip().rstrip("/").replace(".git", "").split("/")
        return parts[-2], parts[-1]
    except IndexError:
        return None, None

# --- Funções de API do GitHub (Atualizadas para usar headers) ---

def listar_branches(owner, repo, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return [branch['name'] for branch in res.json()], None
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code
        if status_code == 404: return [], "Repositório não encontrado. Verifique a URL e o token."
        if status_code == 401: return [], "Acesso não autorizado. Verifique seu GITHUB_TOKEN."
        return [], f"Erro na API do GitHub ({status_code})."
    except requests.exceptions.RequestException as e:
        return [], f"Erro de conexão: {e}"

def obter_arquivos_repo(owner, repo, branch, headers):
    """Busca o conteúdo de arquivos relevantes do repositório."""
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    res = requests.get(tree_url, headers=headers)
    if res.status_code != 200:
        return ""

    tree = res.json().get("tree", [])
    arquivos_texto = ""
    extensoes_relevantes = ['.js', '.py', '.html', '.css', '.java', 'go', 'rb', 'php', 'ts']
    arquivos_filtrados = [f for f in tree if any(f['path'].endswith(ext) for ext in extensoes_relevantes) and f['type'] == 'blob']
    
    for file_data in arquivos_filtrados[:10]:
        blob_res = requests.get(file_data['url'], headers=headers)
        if blob_res.status_code == 200:
            content_b64 = blob_res.json().get('content', '')
            try:
                content_decodificado = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                arquivos_texto += f"\n\n--- ARQUIVO: {file_data['path']} ---\n{content_decodificado}\n"
            except Exception:
                continue
    return arquivos_texto

# --- Rotas da API ---
app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    if not model:
        return jsonify({"error": "Modelo de IA não inicializado."}), 500

    data = request.json
    repo_url = data.get("repo_url")
    user_token = data.get("github_token")

    headers = get_auth_headers(user_token)
    if not headers:
        return jsonify({"error": "Nenhum token do GitHub foi configurado para autenticação."}), 401
    
    if not repo_url:
        return jsonify({"error": "URL do repositório é obrigatória."}), 400

    owner, repo = obter_dono_e_repositorio(repo_url)
    if not owner or not repo:
        return jsonify({"error": "URL do repositório inválida."}), 400

    # CORREÇÃO: Passa os 'headers' para a função
    branches, error = listar_branches(owner, repo, headers)
    if error: return jsonify({"error": error}), 400
    if not branches: return jsonify({"error": "Nenhuma branch encontrada."}), 404

    branch_principal = branches[0]
    print(f"🌿 Analisando a branch principal: {branch_principal}")
    
    # CORREÇÃO: Passa os 'headers' para a função
    codigo_dos_arquivos = obter_arquivos_repo(owner, repo, branch_principal, headers)

    if not codigo_dos_arquivos:
        return jsonify({"error": "Não foi possível encontrar arquivos de código para analisar neste repositório."}), 404

    prompt = f"""
    Você é um engenheiro de software sênior. Sua tarefa é analisar o código de um repositório para gerar um README.md e identificar bugs.
    Conteúdo dos Arquivos: {codigo_dos_arquivos}
    TAREFA: Gere uma resposta JSON com as chaves "readme" e "bugs".
    Para "bugs", crie um array de objetos, cada um com as chaves: "title", "filepath", "severity", "type", "problem", "suggestion", "code_before", e "code_after".
    Responda APENAS com o objeto JSON.
    """

    try:
        print("🤖 Enviando dados para análise completa no Gemini...")
        resposta = model.generate_content(prompt)
        
        # Limpa a resposta para extrair apenas o conteúdo JSON.
        cleaned_text = resposta.text.strip()
        
        # Encontra o início e o fim do objeto JSON.
        json_start = cleaned_text.find('{')
        json_end = cleaned_text.rfind('}') + 1
        
        if json_start != -1 and json_end != 0:
            json_str = cleaned_text[json_start:json_end]
            analysis_json = json.loads(json_str)
        else:
            # Se não encontrar um JSON, lança um erro.
            raise ValueError("Nenhum objeto JSON válido encontrado na resposta.")
        print("✅ Análise completa recebida.")
        return jsonify(analysis_json)
    except Exception as e:
        print(f"❌ Erro ao processar resposta da IA: {e}\nResposta recebida: {resposta.text}")
        return jsonify({"error": "Erro ao gerar análise. A resposta da IA não estava no formato esperado."}), 500

@app.route("/analyze-complexity", methods=["POST"])
def analyze_complexity():
    # ... (Esta rota não precisa de autenticação, permanece a mesma)
    if not model:
        return jsonify({"error": "O modelo de IA não foi inicializado."}), 500
    data = request.json
    code_snippet = data.get("code")
    if not code_snippet or not code_snippet.strip():
        return jsonify({"error": "Nenhum trecho de código foi fornecido."}), 400
    prompt = f"""
    Você é um engenheiro de software sênior, especialista em design de algoritmos.
    Analise o código a seguir:
    ```
    {code_snippet}
    ```
    Forneça sua análise no formato JSON com as chaves "overall_complexity", "bottlenecks" e "suggestions".
    """
    try:
        resposta = model.generate_content(prompt)
        
        # Limpa a resposta para extrair apenas o conteúdo JSON.
        cleaned_text = resposta.text.strip()
        
        # Encontra o início e o fim do objeto JSON.
        json_start = cleaned_text.find('{')
        json_end = cleaned_text.rfind('}') + 1
        
        if json_start != -1 and json_end != 0:
            json_str = cleaned_text[json_start:json_end]
            analysis_json = json.loads(json_str)
        else:
            # Se não encontrar um JSON, lança um erro.
            raise ValueError("Nenhum objeto JSON válido encontrado na resposta.")
            
        return jsonify(analysis_json)
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar análise com o modelo de IA: {str(e)}"}), 500


@app.route("/commit", methods=["POST"])
def commit_readme():
    """
    Recebe o conteúdo do README e faz o commit no repositório do GitHub.
    Usa o token do utilizador para autenticação.
    """
    data = request.json
    repo_url = data.get("repo_url")
    readme_content = data.get("readme_content")
    user_token = data.get("github_token")
    commit_message = data.get("commit_message", "docs: README.md gerado por IA (DocSync AI)") # Mensagem de fallback

    if not all([repo_url, readme_content]):
        return jsonify({"error": "Dados insuficientes para o commit."}), 400

    headers = get_auth_headers(user_token)
    if not headers:
        return jsonify({"error": "Token de autenticação do GitHub é necessário para fazer o commit."}), 401

    owner, repo = obter_dono_e_repositorio(repo_url)
    if not owner or not repo:
        return jsonify({"error": "URL do repositório inválida."}), 400
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
    content_b64 = base64.b64encode(readme_content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": commit_message,
        "content": content_b64,
    }

    print(f"📝 Verificando se README.md já existe em {owner}/{repo}...")
    get_res = requests.get(url, headers=headers)
    
    if get_res.status_code == 200:
        payload["sha"] = get_res.json()["sha"]
        print("   └── README.md encontrado. Será atualizado.")
    elif get_res.status_code != 404:
        print(f"   └── Erro ao buscar README: {get_res.json()}")
        return jsonify({"error": f"Erro ao verificar README existente: {get_res.json().get('message')}"}), 500
    else:
        print("   └── README.md não encontrado. Um novo será criado.")

    print("📤 Enviando commit para o GitHub...")
    put_res = requests.put(url, headers=headers, json=payload)

    if put_res.status_code in [200, 201]:
        commit_url = put_res.json().get('content', {}).get('html_url', '#')
        print(f"✅ Sucesso! Commit realizado: {commit_url}")
        return jsonify({"success": True, "message": "README.md comitado com sucesso!", "url": commit_url})
    else:
        error_details = put_res.json()
        print(f"❌ Erro ao fazer commit: {error_details}")
        return jsonify({"error": f"Erro ao fazer commit no GitHub: {error_details.get('message', 'Erro desconhecido')}"}), 500


@app.route("/pull-request", methods=["POST"])
def pull_request():
    return jsonify({"error": "A funcionalidade de criar Pull Request ainda não foi implementada."}), 501


if __name__ == "__main__":
    app.run(debug=True, port=5000)
