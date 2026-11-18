# Plano de Implementação - Tarefa 7: Renderização Cartográfica e Visualização do Raster CN do Brasil

## 1. Visão Geral e Contexto
O objetivo desta tarefa é transformar a matriz raster GeoTIFF de alta resolução (`resultado_ia/resultado_ia_cn.tif`) em uma peça cartográfica visual de alta qualidade para publicação científica no formato PNG (`resultado_ia/resultado_ia_cn.png`).

A visualização deve representar a distribuição espacial contínua do Número de Curva (Curve Number - CN) sobre o território brasileiro, respeitando rigorosamente a transparência de células sem dados, a proporcionalidade geométrica e a identificação do datum/projeção.

---

## 2. Especificações do Produto Visual

* **Entrada:** `resultado_ia/resultado_ia_cn.tif` (1 banda, Float32, EPSG:5880).
* **Escala de Cores:** Contínua e sequencial, partindo de tons escuros (valores baixos de CN, indicando maior infiltração e menor escoamento) até tons claros (valores altos de CN, indicando menor infiltração e maior escoamento superficial).
  - Utilização do mapa de cores perceptualmente uniforme `viridis` (do roxo escuro ao amarelo brilhante).
* **Tratamento de NoData:** Células com valor `-9999.0` mascaradas com transparência total ($\alpha = 0$), garantindo que apenas a massa territorial do Brasil receba pigmentação.
* **Proporção Geométrica:** Manutenção estrita da razão de aspecto 1:1 (`aspect='equal'`), sem distorções horizontais ou verticais.
* **Anotações Cartográficas:**
  - Título principal contextualizado: *Curva Número (CN) - Brasil*.
  - Indicação explícita do referencial geodésico: *Sistema de Referência: SIRGAS 2000 / Brazil Polyconic (EPSG:5880)*.
  - Barra de cores (legenda) calibrada com escala numérica legível e rótulo explicativo.
* **Resolução de Renderização:** $300\text{ DPI}$ (*Dots Per Inch*), padrão exigido para artefatos e publicações de alto padrão.
* **Destino do Arquivo:** `resultado_ia/resultado_ia_cn.png`.

---

## 3. Mudanças Propostas

### Código e Estrutura de Pastas
- `tarefa_7_visualizacao_raster/prompt.txt`: Registro do comando original enviado pelo usuário.
- `tarefa_7_visualizacao_raster/plano.md`: Este documento de planejamento.
- `tarefa_7_visualizacao_raster/codigo/visualizar_raster.py`: Script Python com pipeline de mascaramento numpy, customização de colormap com canal alfa e renderização em 300 DPI via Matplotlib.
- `tarefa_7_visualizacao_raster/prints/visualizacao_execucao.txt`: Registro de saída e progresso do terminal.
- `tarefa_7_visualizacao_raster/prints/validacao_imagem.txt`: Relatório técnico de auditoria da imagem PNG (resolução, canais RGBA, transparência).
- `tarefa_7_visualizacao_raster/walkthrough.md`: Relatório final documentando a metodologia, tempos de execução, consumo de tokens e custos.
- `resultado_ia/resultado_ia_cn.png`: Imagem PNG resultante em 300 DPI.

---

## 4. Plano de Verificação

### Verificação Automatizada
1. **Execução no `.venv`:** Rodar `visualizar_raster.py` no ambiente virtual com captura de logs.
2. **Auditoria Técnica da Imagem:**
   - Conferir se o arquivo `resultado_ia/resultado_ia_cn.png` existe e possui tamanho condizente com uma renderização de 300 DPI.
   - Inspecionar via `PIL.Image` o modo de cor (RGBA), dimensões em pixels e DPI registrado nos metadados.
   - Avaliar a matriz de transparência: verificar se os pixels correspondentes ao NoData possuem canal $\text{Alpha} = 0$ (transparência total) e se os pixels do Brasil possuem $\text{Alpha} = 255$ (opacidade total).
