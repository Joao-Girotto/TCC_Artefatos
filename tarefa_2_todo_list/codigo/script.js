document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('task-input');
    const addBtn = document.getElementById('add-btn');
    const taskList = document.getElementById('task-list');
    const taskCounter = document.getElementById('task-counter');
    const clearCompletedBtn = document.getElementById('clear-completed-btn');
    const clearSection = document.querySelector('.clear-section');
    
    const filterAll = document.getElementById('filter-all');
    const filterActive = document.getElementById('filter-active');
    const filterCompleted = document.getElementById('filter-completed');
    
    let tasks = JSON.parse(localStorage.getItem('antigravity-tasks')) || [];
    let currentFilter = 'all'; // 'all', 'active', 'completed'
    
    // Salvar no localStorage
    function saveTasks() {
        localStorage.setItem('antigravity-tasks', JSON.stringify(tasks));
    }
    
    // Atualizar estatísticas e visibilidade dos botões
    function updateStats() {
        const activeCount = tasks.filter(t => !t.completed).length;
        const completedCount = tasks.filter(t => t.completed).length;
        
        taskCounter.textContent = `${activeCount} ${activeCount === 1 ? 'pendente' : 'pendentes'}`;
        
        if (completedCount > 0) {
            clearSection.style.display = 'flex';
        } else {
            clearSection.style.display = 'none';
        }
    }
    
    // Renderizar tarefas
    function renderTasks() {
        taskList.innerHTML = '';
        
        let filteredTasks = tasks;
        if (currentFilter === 'active') {
            filteredTasks = tasks.filter(t => !t.completed);
        } else if (currentFilter === 'completed') {
            filteredTasks = tasks.filter(t => t.completed);
        }
        
        if (filteredTasks.length === 0) {
            const emptyMsg = document.createElement('li');
            emptyMsg.className = 'subtitle';
            emptyMsg.style.textAlign = 'center';
            emptyMsg.style.padding = '20px';
            emptyMsg.style.listStyle = 'none';
            emptyMsg.textContent = 'Nenhuma tarefa encontrada.';
            taskList.appendChild(emptyMsg);
            updateStats();
            return;
        }
        
        filteredTasks.forEach(task => {
            const li = document.createElement('li');
            li.className = `task-item ${task.completed ? 'completed' : ''}`;
            li.dataset.id = task.id;
            
            // Gerar IDs únicos para facilitar testes automatizados
            const sanitizedText = task.text.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
            li.id = `task-item-${sanitizedText}`;
            
            li.innerHTML = `
                <div class="task-content" id="task-content-${sanitizedText}">
                    <div class="custom-checkbox">
                        <svg viewBox="0 0 24 24">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    </div>
                    <span class="task-text">${escapeHTML(task.text)}</span>
                </div>
                <button class="delete-btn" id="delete-btn-${sanitizedText}" title="Excluir tarefa">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </button>
            `;
            
            // Evento para alternar conclusão
            li.querySelector('.task-content').addEventListener('click', () => {
                toggleTask(task.id);
            });
            
            // Evento para deletar
            li.querySelector('.delete-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteTask(task.id);
            });
            
            taskList.appendChild(li);
        });
        
        updateStats();
    }
    
    // Função auxiliar de escape HTML
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
    
    // Adicionar tarefa
    function addTask() {
        const text = taskInput.value.trim();
        if (text === '') return;
        
        const newTask = {
            id: Date.now().toString(),
            text: text,
            completed: false
        };
        
        tasks.push(newTask);
        saveTasks();
        taskInput.value = '';
        renderTasks();
        taskInput.focus();
        console.log(`[JS] Tarefa adicionada: "${text}"`);
    }
    
    // Alternar conclusão da tarefa
    function toggleTask(id) {
        tasks = tasks.map(t => {
            if (t.id === id) {
                const newState = !t.completed;
                console.log(`[JS] Tarefa "${t.text}" alterada para concluída = ${newState}`);
                return { ...t, completed: newState };
            }
            return t;
        });
        saveTasks();
        renderTasks();
    }
    
    // Deletar tarefa
    function deleteTask(id) {
        const t = tasks.find(t => t.id === id);
        if (t) {
            console.log(`[JS] Tarefa excluída: "${t.text}"`);
        }
        tasks = tasks.filter(t => t.id !== id);
        saveTasks();
        renderTasks();
    }
    
    // Eventos do teclado e botão
    addBtn.addEventListener('click', addTask);
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addTask();
        }
    });
    
    // Filtros
    filterAll.addEventListener('click', () => {
        setFilter('all', filterAll);
    });
    filterActive.addEventListener('click', () => {
        setFilter('active', filterActive);
    });
    filterCompleted.addEventListener('click', () => {
        setFilter('completed', filterCompleted);
    });
    
    function setFilter(filterType, element) {
        currentFilter = filterType;
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        element.classList.add('active');
        renderTasks();
        console.log(`[JS] Filtro alterado para: ${filterType}`);
    }
    
    // Limpar completadas
    clearCompletedBtn.addEventListener('click', () => {
        tasks = tasks.filter(t => !t.completed);
        saveTasks();
        renderTasks();
        console.log(`[JS] Todas as tarefas concluídas foram apagadas.`);
    });
    
    // Renderização inicial
    renderTasks();
});
