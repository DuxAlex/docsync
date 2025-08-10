document.addEventListener('DOMContentLoaded', () => {
    // --- Seletores de Elementos ---
    const screens = document.querySelectorAll('.screen');
    const menuItems = document.querySelectorAll('.sidebar-menu .menu-item');
    
    // Ecrã de Início
    const analyzeBtn = document.getElementById('analyze-btn');
    const repoUrlInput = document.getElementById('repo-url');
    const githubTokenInput = document.getElementById('github-token');
    const consentCheckbox = document.getElementById('consent-checkbox');
    const showTokenHelpLink = document.getElementById('show-token-help');
    const tokenInstructions = document.getElementById('token-instructions');
    
    // Ecrãs de Resultados
    const repoNameSpans = document.querySelectorAll('.repo-name');
    const readmeContentContainer = document.getElementById('readme-content-container');
    const bugListContainer = document.getElementById('bug-list-container');
    
    // Botões de Ação
    const copyBtn = document.getElementById('copy-readme-btn');
    const exportReadmeBtn = document.getElementById('export-readme-btn');
    const prReadmeBtn = document.getElementById('pr-readme-btn');
    const commitBtn = document.getElementById('commit-readme-btn');

    // Modal de Detalhes de Bugs
    const modalOverlay = document.getElementById('modal-overlay');
    const modalContainer = document.getElementById('modal-container');
    const modalFilepath = document.getElementById('modal-filepath');
    const modalDetails = document.getElementById('modal-details');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const modalCodeBefore = document.getElementById('modal-code-before');
    const modalCodeAfter = document.getElementById('modal-code-after');


    // Análise de Complexidade
    const analyzeComplexityBtn = document.getElementById('analyze-complexity-btn');
    const codeInput = document.getElementById('code-input');
    const complexityResultsContainer = document.getElementById('complexity-results-container');
    const complexitySpinner = document.getElementById('complexity-spinner');
    const complexityError = document.getElementById('complexity-error');
    const complexityOverall = document.getElementById('complexity-overall');
    const complexityBottlenecks = document.getElementById('complexity-bottlenecks');
    const complexitySuggestions = document.getElementById('complexity-suggestions');

    // --- Estado da Aplicação ---
    let currentRepoUrl = '';
    let githubToken = '';
    let fullReadmeContent = '';
    let fullBugList = [];

    // --- Funções de UI ---

    function showScreen(screenId) {
        screens.forEach(screen => {
            if (!screen.classList.contains('hidden')) {
                screen.classList.add('hidden');
            }
        });
        const screenToShow = document.getElementById(screenId);
        if (screenToShow) {
            screenToShow.classList.remove('hidden');
        }
    }

    function toggleButtonSpinner(button, isLoading) {
        const btnText = button.querySelector('.btn-text');
        const spinner = button.querySelector('.spinner');
        if (isLoading) {
            button.disabled = true;
            if (btnText) btnText.classList.add('hidden');
            if (spinner) spinner.classList.remove('hidden');
        } else {
            button.disabled = false;
            if (btnText) btnText.classList.remove('hidden');
            if (spinner) spinner.classList.add('hidden');
        }
    }

    // --- LÓGICA PARA ANÁLISE DE BUGS (ATUALIZADA) ---

    function populateBugList(bugs = []) {
        bugListContainer.innerHTML = ''; // Limpa resultados anteriores
        if (bugs.length === 0) {
            bugListContainer.innerHTML = `<div class="empty-state">Nenhum problema encontrado!</div>`;
            return;
        }

        bugs.forEach(bug => {
            const bugItem = document.createElement('div');
            bugItem.className = 'bug-item';
            
            const severityClass = bug.severity ? bug.severity.toLowerCase() : 'low';

            bugItem.innerHTML = `
                <div class="bug-item-header">
                    <span class="severity-badge ${severityClass}">${bug.severity || 'Info'}</span>
                    <h4 class="bug-title">${bug.title || 'Problema não especificado'}</h4>
                </div>
                <div class="bug-item-body">
                    <span class="bug-filepath">No arquivo: <strong>${bug.filepath || 'N/A'}</strong></span>
                </div>
                <div class="bug-item-footer">
                    <button class="view-details-btn">Ver Detalhes</button>
                </div>
            `;
            bugItem.querySelector('.view-details-btn').dataset.bug = JSON.stringify(bug);
            bugListContainer.appendChild(bugItem);
        });
    }

    function openBugModal(bug) {
        modalFilepath.textContent = bug.filepath || 'Detalhes do Problema';
        
        modalDetails.innerHTML = `
            <h4><i class="fas fa-exclamation-triangle"></i> Problema Encontrado</h4>
            <p>${bug.problem || 'Não descrito.'}</p>
            <hr>
            <h4><i class="fas fa-lightbulb"></i> Sugestão da IA</h4>
            <p>${bug.suggestion || 'Nenhuma sugestão fornecida.'}</p>
        `;

        modalCodeBefore.innerHTML = '';
        modalCodeAfter.innerHTML = '';

        const codeBeforeEl = document.createElement('code');
        codeBeforeEl.className = 'language-javascript'; 
        codeBeforeEl.textContent = bug.code_before || "Código original não fornecido.";
        modalCodeBefore.appendChild(codeBeforeEl);

        const codeAfterEl = document.createElement('code');
        codeAfterEl.className = 'language-javascript';
        codeAfterEl.textContent = bug.code_after || "Sugestão de código não fornecida.";
        modalCodeAfter.appendChild(codeAfterEl);

        if (typeof hljs !== 'undefined') {
            hljs.highlightElement(codeBeforeEl);
            hljs.highlightElement(codeAfterEl);
        }

        modalOverlay.classList.remove('hidden');
        modalContainer.classList.remove('hidden');
    }

    function closeBugModal() {
        modalOverlay.classList.add('hidden');
        modalContainer.classList.add('hidden');
    }

    // --- Event Listeners ---

    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetScreen = item.getAttribute('data-target');
            showScreen(targetScreen);
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });

    analyzeBtn.addEventListener('click', async () => {
        currentRepoUrl = repoUrlInput.value;
        githubToken = githubTokenInput.value;

        if (!currentRepoUrl) {
            alert('Por favor, insira a URL de um repositório.');
            return;
        }

        if (!githubToken) {
            alert('Por favor, insira seu token do GitHub.');
            return;
        }

        toggleButtonSpinner(analyzeBtn, true);
        try {
            const response = await fetch("http://localhost:5000/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ repo_url: currentRepoUrl, token: githubToken })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);

            fullReadmeContent = data.readme || "# README não gerado";
            fullBugList = data.bugs || [];
            
            repoNameSpans.forEach(span => span.textContent = currentRepoUrl.split('/').slice(-2).join('/'));
            readmeContentContainer.innerHTML = marked.parse(fullReadmeContent);
            populateBugList(fullBugList);

            showScreen('readme-screen');
            menuItems.forEach(i => i.classList.remove('active'));
            document.querySelector('.menu-item[data-target="readme-screen"]').classList.add('active');

        } catch (error) {
            alert(`Erro na análise: ${error.message}`);
        } finally {
            toggleButtonSpinner(analyzeBtn, false);
        }
    });
    
    consentCheckbox.addEventListener('change', () => {
        analyzeBtn.disabled = !consentCheckbox.checked;
    });

    bugListContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('view-details-btn')) {
            const bugData = JSON.parse(e.target.dataset.bug);
            openBugModal(bugData);
        }
    });
    closeModalBtn.addEventListener('click', closeBugModal);
    modalOverlay.addEventListener('click', closeBugModal);

    showTokenHelpLink.addEventListener('click', (e) => {
        e.preventDefault();
        tokenInstructions.classList.toggle('hidden');
    });

    exportReadmeBtn.addEventListener('click', () => {
        if (!fullReadmeContent) return;
        const blob = new Blob([fullReadmeContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'README.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    commitBtn.addEventListener('click', async () => {
        if (!currentRepoUrl || !fullReadmeContent || !githubToken) {
            alert('Repositório, README ou token não disponíveis. Analise primeiro.');
            return;
        }

        const commitMessage = prompt("Digite a mensagem de commit:", "docs: update README.md by DocSync AI");
        if (!commitMessage) return; // User cancelled

        toggleButtonSpinner(commitBtn, true);
        try {
            const response = await fetch("http://localhost:5000/commit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    repo_url: currentRepoUrl, 
                    readme_content: fullReadmeContent, 
                    token: githubToken,
                    commit_message: commitMessage
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            alert('Commit realizado com sucesso!');
        } catch (error) {
            alert(`Erro ao fazer commit: ${error.message}`);
        } finally {
            toggleButtonSpinner(commitBtn, false);
        }
    });

    prReadmeBtn.addEventListener('click', async () => {
        alert('A funcionalidade de criar Pull Request ainda não foi implementada no backend.');
    });

    analyzeComplexityBtn.addEventListener('click', async () => {
        const code = codeInput.value;
        if (!code.trim()) return alert("Cole um código para analisar.");

        complexitySpinner.classList.remove('hidden');
        complexityError.classList.add('hidden');
        complexityResultsContainer.classList.add('hidden');
        analyzeComplexityBtn.disabled = true;

        try {
            const response = await fetch("http://localhost:5000/analyze-complexity", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            if (!data.overall_complexity) throw new Error("A resposta da IA não continha uma análise válida.");

            complexityOverall.textContent = data.overall_complexity;

            // **CORREÇÃO**: Garante que o input para 'marked' seja uma string.
            const bottlenecksContent = Array.isArray(data.bottlenecks) ? data.bottlenecks.join('\n') : (data.bottlenecks || "");
            const suggestionsContent = Array.isArray(data.suggestions) ? data.suggestions.join('\n') : (data.suggestions || "");

            complexityBottlenecks.innerHTML = marked.parse(bottlenecksContent);
            complexitySuggestions.innerHTML = marked.parse(suggestionsContent);
            
            complexityResultsContainer.classList.remove('hidden');
        } catch (err) {
            complexityError.textContent = `Erro: ${err.message}`;
            complexityError.classList.remove('hidden');
        } finally {
            complexitySpinner.classList.add('hidden');
            analyzeComplexityBtn.disabled = false;
        }
    });

    showScreen('input-screen');
    
    // --- INICIALIZAÇÃO DO PARTICLES.JS ---
    if (document.getElementById('particles-js')) {
        particlesJS('particles-js', {
            "particles": {
                "number": { "value": 60, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#ffffff" },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.5, "random": true },
                "size": { "value": 3, "random": true },
                "line_linked": { "enable": true, "distance": 150, "color": "#ffffff", "opacity": 0.4, "width": 1 },
                "move": { "enable": true, "speed": 2, "direction": "none", "random": false, "straight": false, "out_mode": "out", "bounce": false }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": { "onhover": { "enable": true, "mode": "repulse" }, "onclick": { "enable": true, "mode": "push" }, "resize": true },
                "modes": { "repulse": { "distance": 100, "duration": 0.4 }, "push": { "particles_nb": 4 } }
            },
            "retina_detect": true
        });
    }
});
