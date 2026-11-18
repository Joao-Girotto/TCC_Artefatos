# Plano de Implementação - Tarefa 6: Rasterização Espacial de Polígonos de Curve Number (CN) para GeoTIFF

## 1. Visão Geral e Contexto
O objetivo desta tarefa é transformar os dados vetoriais da Base Hidrográfica Otorgada reprojetada (`dados_processados/BHO_CN_5880.gpkg`, contendo 1.305.955 polígonos) em um raster matricial contínuo no formato GeoTIFF cobrindo o território brasileiro.

O valor matricial de cada célula corresponderá ao campo `Ave_CN` (média ponderada do Número de Curva - Curve Number) do polígono que contém o centro do pixel.

---

## 2. Especificações Técnicas do Produto Cartográfico

* **Sistema de Referência de Coordenadas (CRS):** SIRGAS 2000 / Brazil Polyconic (`EPSG:5880`).
* **Resolução Espacial:** Pixel de $1000\text{ m} \times 1000\text{ m}$.
* **Extensão Espacial (Bounding Box):**
  - $X_{\min} = 2.781.000\text{ m}$, $X_{\max} = 7.120.000\text{ m}$ (Largura: $4.339.000\text{ m} \rightarrow 4.339\text{ colunas}$)
  - $Y_{\min} = 6.263.000\text{ m}$, $Y_{\max} = 10.587.000\text{ m}$ (Altura: $4.324.000\text{ m} \rightarrow 4.324\text{ linhas}$)
  - Origem superior esquerda: $(2.781.000, 10.587.000)$.
* **Dimensões da Matriz:** $4.339 \text{ colunas} \times 4.324 \text{ linhas}$ ($18.761.836\text{ pixels}$).
* **Tipo de Dado:** `Float32` (4 bytes por pixel).
* **Valor NoData:** `-9999.0` para áreas fora dos polígonos da hidrografia/território.
* **Critério de Amostragem:** Centróide de pixel (`all_touched=False` no algoritmo de rasterização do GDAL/Rasterio).
* **Destino do Arquivo:** `resultado_ia/resultado_ia_cn.tif`.

---

## 3. Desafios Técnicos e Estratégia de Engenharia

> [!IMPORTANT]
> **Gestão Eficiente de Memória em Processamento Vetor-Raster:**
> A matriz de saída possui cerca de 18,76 milhões de células em Float32, ocupando apenas $\approx 71,6\text{ MB}$ de memória RAM.
> No entanto, o carregamento das geometrias de 1,3 milhão de polígonos em memória simultânea para renderização vetorial pode degradar a performance.
>
> **Solução Arquitetural:**
> - Alocação direta da matriz numpy preenchida inicialmente com `-9999.0`.
> - Leitura streaming por lotes (*chunks* de 100.000 feições) carregando estritamente as colunas necessárias (`Ave_CN` e `geometry`).
> - Queima incremental (*in-place rasterization*) diretamente na matriz pré-alocada usando `rasterio.features.rasterize(shapes, out=arr, all_touched=False)`.
> - Gravação em formato GeoTIFF otimizado com compressão DEFLATE sem perdas e blocos ladrilhados (`tiled=True`), reduzindo o I/O em disco e permitindo abertura instantânea em softwares GIS (QGIS/ArcGIS).

---

## 4. Mudanças Propostas

### Código e Estrutura de Pastas
- `tarefa_6_rasterizacao_cn/prompt.txt`: Registro do comando original do usuário.
- `tarefa_6_rasterizacao_cn/plano.md`: Este documento de planejamento.
- `tarefa_6_rasterizacao_cn/codigo/rasterizar_cn.py`: Script Python autônomo que executa a rasterização em streaming e gera o arquivo GeoTIFF.
- `tarefa_6_rasterizacao_cn/prints/rasterizacao_execucao.txt`: Registro de saída e progresso no terminal.
- `tarefa_6_rasterizacao_cn/prints/validacao_raster.txt`: Relatório de auditoria e validação dos metadados e estatísticas do raster gerado.
- `tarefa_6_rasterizacao_cn/walkthrough.md`: Relatório final documentando a metodologia, tempos de execução, consumo de tokens e custos.
- `resultado_ia/resultado_ia_cn.tif`: Arquivo raster GeoTIFF resultante.

---

## 5. Plano de Verificação

### Verificação Automatizada
1. **Execução no Ambiente `.venv`:** Rodar o script `rasterizar_cn.py` com registro de logs.
2. **Auditoria Técnica do Raster:**
   - Conferir se o arquivo `resultado_ia/resultado_ia_cn.tif` existe e está íntegro.
   - Conferir dimensões exatas: `4339` colunas $\times$ `4324` linhas.
   - Conferir CRS: `EPSG:5880`.
   - Conferir tipo de dado: `float32`.
   - Conferir valor NoData: `-9999.0`.
   - Conferir limites geográficos da matriz: $X \in [2.781.000, 7.120.000]$, $Y \in [6.263.000, 10.587.000]$.
   - Conferir estatísticas dos pixels válidos (mínimo, máximo, média e desvio padrão dentro da faixa esperada do Curve Number, entre 0 e 100).
