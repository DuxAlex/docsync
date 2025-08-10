# DocSync AI

DocSync AI é uma aplicação web que analisa o código de um repositório GitHub e gera um README.md com base na análise do código e identificação de bugs potenciais. Ela utiliza a API do GitHub para obter informações do repositório e o Google Gemini para processamento de linguagem natural, análise de código e geração de conteúdo.

## Funcionalidades

* **Análise de Repositório:**  Recebe a URL de um repositório GitHub (público ou privado, com autenticação) e analisa seu conteúdo.
* **Geração de README:** Gera um README.md com uma descrição concisa do projeto baseada no código analisado.
* **Detecção de Bugs:** Identifica potenciais bugs no código, fornecendo informações detalhadas sobre cada um, incluindo sugestões de correção.
* **Análise de Complexidade:** Avalia a complexidade algorítmica de trechos de código, apontando gargalos e sugestões de otimização.
* **Commit de README:** Permite comitar o README.md gerado diretamente para o repositório GitHub, usando um token de acesso.      

## Tecnologias Utilizadas

* **Frontend:** HTML, CSS, JavaScript, marked.js, particles.js
* **Backend:** Python, Flask, requests, google-generativeai, dotenv, flask-cors
* **IA:** Google Gemini

## Instalação e Execução

1. **Requisitos:**
    * Python 3.9+
    * `pip install -r requirements.txt`
    * Chaves de API (GOOGLE_API_KEY, GITHUB_TOKEN). Veja as variáveis de ambiente abaixo.

2. **Variáveis de Ambiente:**
    * `GITHUB_TOKEN`: Um token de acesso pessoal do GitHub.  Necessário para acesso a repositórios privados.
    * `GEMINI_API_KEY`: Sua chave de API do Google Gemini.

3. **Execução:**
    * `python app.py`

A aplicação irá iniciar no servidor local na porta 5000.

## Bugs Encontrados na Análise do Código

Durante a análise do código fonte, foram identificados os seguintes problemas:

* **Nenhum bug crítico foi detectado no código fornecido.** O código demonstra boas práticas de tratamento de erros e utilização da API do Github.  A lógica principal da aplicação está bem estruturada e eficiente, com tratamento adequado de possíveis falhas na comunicação com a API do GitHub e o modelo de IA.  A integração com o Gemini é robusta, com tratamento de exceções para garantir 
a estabilidade da aplicação.

## Potenciais Melhorias

* **Tratamento de Erros:** Embora o código já tenha um bom tratamento de erros, pode ser aprimorado com mensagens mais informativas e específicas para o usuário.
* **Escalabilidade:**  Implementar mecanismos para lidar com grandes repositórios, otimizando o tempo de processamento.
* **Interface do Usuário:** Aprimorar a interface do usuário com recursos adicionais, como a visualização do código antes e depois da sugestão de correção (isso já está parcialmente implementado no modal, porém necessita de uma melhor integração para mostrar todas as alterações).
* **Integração com outros provedores de IA:**  Possibilitar a escolha de outros modelos de IA, além do Gemini.
* **Funcionalidades Adicionais:** Adicionar funcionalidades como a análise de métricas de código (complexidade ciclomática, etc.), geração de testes unitários e/ou documentação adicional.
* **Limite de arquivos:** Implementar um limite mais robusto para a quantidade de arquivos analisados por requisição, além do limite arbitrário atual de 10 arquivos.



## Contribuições

Contribuições são bem-vindas!  Abra uma issue ou um pull request no repositório do GitHub.
