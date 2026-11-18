# Plano de Implementação - Tarefa 8: Aplicação Web Interativa (Streamlit) para Exploração Espacial e Estatística de Curve Number

## 1. Visão Geral e Contexto
O objetivo desta tarefa é construir uma aplicação analítica e interativa em **Streamlit**, integrando a camada matricial gerada na Tarefa 6 (`resultado_ia/resultado_ia_cn.tif`) com a base de dados atributiva da Base Hidrográfica Otorgada da ANA (`dados_originais/BHO_2014_CN.shp`).

A aplicação permitirá que pesquisadores e tomadores de decisão explorem a distribuição do Número de Curva (CN) no território brasileiro por meio de:
1. **Mapa Interativo (Folium/Leaflet):** com suporte completo a zoom, pan, controle de camadas e sobreposição da matriz raster georreferenciada.
2. **Painel de Inteligência Analítica e Estatística (Plotly):** contendo métricas síntese, gráficos de distribuição de frequência (histogramas), diagramas de dispersão/boxplot e tabelas dinâmicas de microbacias.
3. **Validação Agêntica com Subagente de Navegador:** teste automatizado do servidor web em execução local (`http://localhost:8501`), interagindo com os elementos da interface e capturando o registro funcional.

---

## 2. Arquitetura da Solução

* **Backend / Servidor:** Streamlit (`v1.40+`) rodando no ambiente virtual `.venv` na porta `8501`.
* **Módulo Geoespacial Web:** Reprojeção em tempo de execução via `rasterio.warp` para grade WGS84 (`EPSG:4326`) e conversão para camada `folium.raster_layers.ImageOverlay` com canal alfa transparente para áreas NoData.
* **Módulo de Estatística Tabular:** Carregamento otimizado de metadados atributivos com cache do Streamlit (`@st.cache_data`), garantindo resposta instantânea na interface sem estouro de memória.
* **Componentes Interativos:**
  - Seletor de visualização (Visão Geral, Mapa Espacial, Análise Estatística, Explorador de Bacias).
  - Filtros dinâmicos por faixas de CN e contagem de células.
  - Gráficos responsivos Plotly com tooltips interativos.

---

## 3. Mudanças Propostas

### Código e Estrutura de Pastas
- `tarefa_8_dashboard_interativo/prompt.txt`: Registro do comando original do usuário.
- `tarefa_8_dashboard_interativo/plano.md`: Este documento de planejamento.
- `tarefa_8_dashboard_interativo/codigo/app.py`: Código-fonte completo da aplicação Streamlit.
- `tarefa_8_dashboard_interativo/codigo/requirements.txt`: Registro das dependências e versões instaladas.
- `tarefa_8_dashboard_interativo/prints/server_logs.txt`: Log de inicialização e requisições do servidor Streamlit.
- `tarefa_8_dashboard_interativo/prints/dashboard_view.png`: Captura de tela gerada pelo subagente de navegador.
- `tarefa_8_dashboard_interativo/walkthrough.md`: Relatório de execução, tempos, tokens e custos.

---

## 4. Plano de Verificação

### Verificação Automatizada
1. **Inicialização do Servidor Local:**
   Subir o Streamlit em segundo plano via `run_command` com `IsDaemon: true`:
   `streamlit run app.py --server.port 8501 --server.headless true`
2. **Validação com Subagente de Navegador (`browser_subagent`):**
   - Delegar a abertura e inspeção da URL `http://localhost:8501` ao subagente do navegador.
   - Navegar pelas abas do dashboard, inspecionar os elementos renderizados (mapa Folium, gráficos Plotly, métricas).
   - Capturar prints de tela e confirmar que a aplicação funciona perfeitamente sem erros de JavaScript ou Python.
