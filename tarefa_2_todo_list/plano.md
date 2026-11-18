# Desenvolvimento de To-Do List Premium e Validação por Navegador Interno

Este projeto consiste em desenvolver uma aplicação web de To-Do List utilizando HTML, CSS (Vanilla) e JavaScript. A interface terá uma estética moderna e premium (modo escuro, glassmorfismo, micro-animações, design responsivo) e será validada abrindo um servidor local HTTP e usando o agente de navegação para interações automatizadas de inserção de tarefas.

## User Review Required

> [!IMPORTANT]
> O teste automatizado utilizará o subagente do navegador para abrir a página hospedada localmente e interagir adicionando 3 tarefas. O vídeo da interação será salvo automaticamente e o log da sessão será registrado em arquivo de texto.

## Proposed Changes

### Interface do Usuário (HTML/CSS/JS)

#### [NEW] [index.html](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_2_todo_list/codigo/index.html)
- Estrutura semântica para a To-Do List contendo cabeçalho, painel de inserção, filtros (Todas, Ativas, Concluídas), lista de tarefas dinâmicas e estatísticas.

#### [NEW] [style.css](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_2_todo_list/codigo/style.css)
- Folha de estilos premium com variáveis CSS para cores customizadas, gradientes suaves, efeitos de desfoque de fundo (Glassmorphism), transições suaves em hover/focus e animações de entrada/conclusão de tarefas.
- Utilização da fonte "Inter" obtida via Google Fonts.

#### [NEW] [script.js](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_2_todo_list/codigo/script.js)
- Lógica JS pura (Vanilla ES6) para gerenciamento de estado (adicionar, alternar conclusão, remover, filtrar tarefas).
- Persistência básica no `localStorage` para simular uma aplicação profissional.

### Infraestrutura e Testes

#### [NEW] [plano.md](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_2_todo_list/plano.md)
- Cópia do plano de implementação para o workspace do usuário.

## Verification Plan

### Automated Verification
- Subir um servidor HTTP local simples com Python na pasta `codigo/`:
  `python3 -m http.server 8080`
- Utilizar a ferramenta `browser_subagent` para:
  1. Acessar `http://localhost:8080`
  2. Adicionar 3 tarefas sequencialmente (ex: "Configurar ambiente espacial", "Testar dependências GDAL", "Revisar escrita do TCC").
  3. Marcar uma delas como concluída.
  4. Filtrar as tarefas para demonstrar o funcionamento dos filtros.
  5. Fechar o servidor e registrar o log de interações em `prints/log_navegador.txt`.
