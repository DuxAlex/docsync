# Resumo do Projeto: docsync

## Visão Geral

`docsync` é uma aplicação web full-stack projetada para analisar repositórios de código-fonte do GitHub. A aplicação utiliza a API Gemini do Google para gerar documentação (`README.md`) e identificar potenciais bugs no código. O frontend permite que o usuário insira a URL de um repositório e um token do GitHub, e o backend Flask processa a análise e permite fazer o commit do `README.md` gerado de volta para o repositório.

## Arquitetura

- **Frontend**: `index.html`, `style.css`, `script.js`.
  - Uma interface de página única para inserir a URL do repositório e o token do GitHub.
  - Exibe os resultados da análise (README sugerido e bugs encontrados).
  - Permite ao usuário acionar o commit do novo README.

- **Backend**: `app.py` (Flask)
  - **API**: Expõe endpoints para `/analyze`, `/analyze-complexity`, e `/commit`.
  - **Integração com GitHub**: Usa a API REST do GitHub para listar branches, buscar a árvore de arquivos e fazer commits.
  - **Inteligência Artificial**: Conecta-se à API Gemini (`gemini-1.5-flash-latest`) para processar o código e gerar a análise.
  - **Segurança**: Utiliza variáveis de ambiente (`.env`) para gerenciar chaves de API (`GITHUB_TOKEN`, `GEMINI_API_KEY`).

- **Dependências Principais**:
  - `flask`: Micro-framework web.
  - `google-generativeai`: Cliente Python para a API Gemini.
  - `requests`: Para fazer chamadas à API do GitHub.
  - `python-dotenv`: Para carregar variáveis de ambiente.
  - `flask-cors`: Para permitir requisições do frontend.

## Fluxo de Trabalho Principal

1.  O usuário insere a URL de um repositório do GitHub e um token de autenticação no frontend.
2.  O frontend envia uma requisição POST para o endpoint `/analyze` do backend.
3.  O backend busca os arquivos de código do repositório especificado usando a API do GitHub.
4.  O conteúdo dos arquivos é enviado para a API Gemini com um prompt instruindo-a a gerar um `README.md` e uma lista de bugs em formato JSON.
5.  O backend recebe a resposta JSON, processa-a e a retorna para o frontend.
6.  O frontend exibe o `README.md` e os bugs para o usuário.
7.  O usuário pode então clicar em um botão para enviar o conteúdo do README para o endpoint `/commit`, que o salva de volta no repositório do GitHub.
