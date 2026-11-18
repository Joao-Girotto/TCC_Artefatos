# Plano de Implementação - Tarefa 9: Pipeline Completo de Geoprocessamento de Ponta a Ponta (Reprojeção, Rasterização e Aplicação Web)

## 1. Visão Geral e Contexto
O objetivo da **Tarefa 9** é consolidar e re-executar de forma 100% automatizada e integrada todo o fluxo de trabalho do TCC desenvolvido entre as Tarefas 5 e 8, partindo exclusivamente do Shapefile bruto original (`dados_originais/BHO_2014_CN.shp`, contendo 1.305.955 polígonos em SAD 69) até a disponibilização de uma aplicação web interativa em `aplicacao/` funcionando no navegador.

---

## 2. Especificações dos Produtos Finais

1. **Vetor Reprojetado (GeoPackage):**
   - Destino: `dados_processados/BHO_CN_5880.gpkg`
   - CRS: SIRGAS 2000 / Brazil Polyconic (`EPSG:5880`)
   - Geometrias: `MultiPolygon` em conformidade estrita com o padrão OGC
   - Integridade: 100% das feições (1.305.955) e todos os 8 atributos originais preservados.

2. **Raster GeoTIFF de Curve Number:**
   - Destino: `resultado_ia/resultado_ia_cn.tif`
   - CRS: `EPSG:5880`
   - Resolução: $1000\text{ m} \times 1000\text{ m}$ ($1\text{ km} \times 1\text{ km}$)
   - Extensão: $X \in [2.781.000, 7.120.000]\text{ m}$; $Y \in [6.263.000, 10.587.000]\text{ m}$
   - Dimensão: $4.339\text{ colunas} \times 4.324\text{ linhas}$ ($18.761.836\text{ células}$)
   - Tipo de Dado: `Float32`, com NoData configurado em `-9999.0`
   - Critério de Amostragem: Valor do polígono que contém o centro do pixel (`all_touched=False`).

3. **Aplicação Streamlit em `aplicacao/`:**
   - Localização: `aplicacao/app.py`
   - Mapa Interativo: Suporte completo a zoom, pan, camadas base e sobreposição raster georreferenciada.
   - Indicadores Estatísticos Mandatórios:
     1. Número de pixels válidos
     2. Área em $\text{km}²$
     3. Valor Mínimo de CN
     4. Valor Máximo de CN
     5. Média de CN
     6. Desvio-padrão populacional de CN ($\sigma = \sqrt{\frac{1}{N}\sum(x_i - \mu)^2}$, com `ddof=0`)
   - Execução no navegador: Servidor local ativo na porta 8501 e validado por automação de navegador com captura de telas.

---

## 3. Arquitetura e Engenharia de Execução

> [!IMPORTANT]
> **Autonomia e Registro de Falhas (Self-Correction Log):**
> O pipeline será executado por um script orquestrador unificado (`pipeline_completo.py`) que encadeia a reprojeção vetorial em lote, a queima raster in-place e a validação do produto.
> Caso ocorra qualquer inconsistência, advertência ou falha em tempo de execução, o agente documentará o log do erro, o diagnóstico da causa-raiz e o patch aplicado.

---

## 4. Mudanças Propostas

### Código e Estrutura de Pastas
- `tarefa_9_pipeline_completo/prompt.txt`: Registro do comando original do usuário.
- `tarefa_9_pipeline_completo/plano.md`: Este documento de planejamento.
- `tarefa_9_pipeline_completo/codigo/pipeline_completo.py`: Script unificado para executar a reprojeção e rasterização do início ao fim com medição de desempenho e integridade.
- `aplicacao/app.py`: Código-fonte da aplicação Streamlit contendo todos os 6 indicadores estatísticos explícitos e o mapa interativo.
- `tarefa_9_pipeline_completo/codigo/test_aplicacao.py`: Script Playwright para verificação funcional automatizada no navegador headless.
- `tarefa_9_pipeline_completo/prints/pipeline_execucao.txt`: Log completo da execução de ponta a ponta do pipeline.
- `tarefa_9_pipeline_completo/prints/validacao_produtos.txt`: Relatório técnico de auditoria do GeoPackage e do GeoTIFF gerados.
- `tarefa_9_pipeline_completo/prints/app_browser_view.png`: Captura de tela da aplicação em funcionamento no navegador.
- `tarefa_9_pipeline_completo/walkthrough.md`: Relatório final documentando a metodologia, tempos de execução, consumo de tokens e custos.
- Atualização em `TCC_Escrita.md`: Inclusão do novo bloco da Tarefa 9, atualização da tabela de cronograma e nota de pesquisa metodológica.

---

## 5. Plano de Verificação

### Verificação Automatizada
1. **Pipeline de Dados:** Rodar `pipeline_completo.py` no ambiente `.venv` e validar a integridade estrutural do `BHO_CN_5880.gpkg` e do `resultado_ia_cn.tif`.
2. **Servidor Streamlit:** Iniciar o servidor com `IsDaemon: true` na porta 8501 a partir de `aplicacao/app.py`.
3. **Teste no Navegador:** Executar `test_aplicacao.py` via Playwright para verificar se todos os 6 indicadores numéricos foram calculados corretamente, interagir com o mapa (zoom) e capturar a tela comprovando o funcionamento.
