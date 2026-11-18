# Relatório de Execução - Tarefa 8: Aplicação Web Interativa (Streamlit) para Exploração Espacial e Estatística de Curve Number

## 1. Visão Geral
A **Tarefa 8** consistiu no desenvolvimento de uma aplicação web analítica e interativa utilizando o framework **Streamlit**, integrando a camada matricial do território brasileiro (`resultado_ia/resultado_ia_cn.tif`) a um mapa interativo com suporte a zoom e pan (Folium), acompanhado de painéis de inteligência estatística (Plotly) baseados na tabela original do Shapefile de microbacias da ANA (`dados_originais/BHO_2014_CN.shp`). A aplicação foi empacotada com um arquivo `requirements.txt`, executada em servidor local (`http://localhost:8501`) e validada de ponta a ponta no navegador.

---

## 2. Métricas de Execução e Custo Agêntico

### Tempo de Execução
* **Momento do Prompt:** 2026-11-13T20:36:14-03:00 (23:36:14 UTC)
* **Momento de Conclusão:** 2026-11-13T20:43:25-03:00 (23:43:25 UTC)
* **Tempo Total de Interação Agêntica:** **7 minutos e 11 segundos** (englobando instalação de dependências, desenvolvimento do app, inicialização do servidor e validação automatizada no navegador)

### Consumo de Tokens e Estimativa de Custo (Gemini 3.8 Flash)
Com base na extração do transcript oficial (`transcript.jsonl`) a partir do step 200:

| Métrica de Token | Quantidade | Preço Base (/ 1M tokens) | Custo Estimado (USD) |
|---|---|---|---|
| **Input Tokens (não cacheados)** | 108.402 | \$0,075 | \$0,00813 |
| **Cache Read Tokens (Prompt Cache)** | 6.027.938 | \$0,01875 | \$0,11302 |
| **Output Tokens (Raciocínio & Ações)** | 18.516 | \$0,300 | \$0,00555 |
| **Total de Tokens Processados** | **6.154.856** | - | **\$0,12670** (~R\$ 0,72) |

---

## 3. Artefatos Produzidos
* **Comando do Usuário:** [prompt.txt](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/prompt.txt)
* **Plano de Implementação:** [plano.md](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/plano.md)
* **Código da Aplicação Streamlit:** [app.py](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/codigo/app.py)
* **Arquivo de Dependências:** [requirements.txt](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/codigo/requirements.txt)
* **Script de Teste de Navegador:** [test_dashboard.py](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/codigo/test_dashboard.py)
* **Logs do Servidor Streamlit:** [server_logs.txt](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/prints/server_logs.txt)
* **Log do Teste de Navegador:** [log_navegador.txt](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/prints/log_navegador.txt)
* **Captura de Tela do Dashboard (Mapa com Zoom):** [dashboard_view.png](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/prints/dashboard_view.png)

---

## 4. O Que Foi Feito

1. **Gestão de Dependências e Requirements:**
   - Instalação no ambiente virtual `.venv` das bibliotecas `streamlit`, `folium`, `streamlit-folium`, `plotly`, `pydeck`, `altair` e `playwright`.
   - Geração de [requirements.txt](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/codigo/requirements.txt) com as versões exatas de cada dependência.
2. **Desenvolvimento da Aplicação Streamlit ([app.py](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/codigo/app.py)):**
   - **Módulo de Mapa Interativo (Folium):**
     - Reprojeção em tempo de execução via `rasterio.warp.reproject` do raster SIRGAS 2000 / Polyconic para a grade WGS84 (`EPSG:4326`).
     - Geração de matriz RGBA com canal alfa transparente para áreas NoData e escala contínua Viridis.
     - Sobreposição via `folium.raster_layers.ImageOverlay` com suporte a zoom in/out, pan, alternância de mapas-base (CartoDB Positron, Dark Matter, OpenStreetMap), mini-mapa e tela cheia.
   - **Painel Analítico de Microbacias (Plotly):**
     - Carregamento de alta performance via `@st.cache_data` dos dados tabulares da ANA sem geometria (evitando consumo desnecessário de memória).
     - Cards de métricas principais (1.305.955 polígonos, média 60.68, min 6.0, max 100.0, desvio padrão 16.22).
     - Histograma interativo com linha vertical na média nacional.
     - Boxplot comparativo de valores extremos (`Min_CN`, `Ave_CN`, `Max_CN`).
     - Gráfico de dispersão relacionando tamanho de microbacia (`Count`) e variabilidade (`StdDv_CN`).
     - Matriz de correlação de Pearson entre todas as variáveis hidrológicas.
   - **Explorador Tabular:**
     - Tabela dinâmica com ordenação e filtros interativos por faixa de valores, acompanhada de botão de exportação para CSV.
3. **Execução do Servidor e Validação Automatizada de Navegador:**
   - O servidor Streamlit foi iniciado em segundo plano na porta padrão `8501`.
   - Um script de automação Playwright executou o ciclo de validação no navegador headless:
     1. Conectou-se a `http://localhost:8501` e verificou a montagem completa da árvore DOM em 7,99 segundos.
     2. Validou a presença de todos os 5 cartões de métricas.
     3. Confirmou a renderização do iframe do mapa interativo Folium e realizou uma ação de zoom com a roda do mouse.
     4. Alternou dinamicamente entre as abas, inspecionando os gráficos Plotly e a tabela de dados.
     5. Salvou a captura de tela de validação em [dashboard_view.png](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_8_dashboard_interativo/prints/dashboard_view.png).
