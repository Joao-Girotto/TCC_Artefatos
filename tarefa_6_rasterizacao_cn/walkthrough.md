# Relatório de Execução - Tarefa 6: Rasterização Espacial de Curve Number (CN) para GeoTIFF

## 1. Visão Geral
A **Tarefa 6** consistiu na conversão matricial contínua dos dados vetoriais da Base Hidrográfica Otorgada (`dados_processados/BHO_CN_5880.gpkg`, contendo 1.305.955 polígonos) em um raster GeoTIFF representando o valor de Curve Number (`Ave_CN`) para todo o território brasileiro, sob a projeção métrica SIRGAS 2000 / Brazil Polyconic (`EPSG:5880`).

---

## 2. Métricas de Execução e Custo Agêntico

### Tempo de Execução
* **Momento do Prompt:** 2026-11-13T20:18:02-03:00 (23:18:02 UTC)
* **Momento de Conclusão:** 2026-11-13T20:23:05-03:00 (23:23:05 UTC)
* **Tempo Total de Interação Agêntica:** **5 minutos e 3 segundos**
* **Tempo de Execução do Script:** **110,33 segundos** (~1,84 minutos para rasterizar 1,3 milhão de polígonos e gravar o GeoTIFF)

### Consumo de Tokens e Estimativa de Custo (Gemini 3.8 Flash)
Com base na extração do transcript oficial (`transcript.jsonl`) a partir do step 103:

| Métrica de Token | Quantidade | Preço Base (/ 1M tokens) | Custo Estimado (USD) |
|---|---|---|---|
| **Input Tokens (não cacheados)** | 52.213 | \$0,075 | \$0,00392 |
| **Cache Read Tokens (Prompt Cache)** | 1.510.503 | \$0,01875 | \$0,02832 |
| **Output Tokens (Raciocínio & Ações)** | 17.064 | \$0,300 | \$0,00512 |
| **Total de Tokens Processados** | **1.579.780** | - | **\$0,03736** (~R\$ 0,21) |

---

## 3. Artefatos Produzidos
* **Comando do Usuário:** [prompt.txt](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_6_rasterizacao_cn/prompt.txt)
* **Plano de Implementação:** [plano.md](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_6_rasterizacao_cn/plano.md)
* **Script de Rasterização:** [rasterizar_cn.py](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_6_rasterizacao_cn/codigo/rasterizar_cn.py)
* **Log da Execução Principal:** [rasterizacao_execucao.txt](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_6_rasterizacao_cn/prints/rasterizacao_execucao.txt)
* **Relatório de Auditoria:** [validacao_raster.txt](file:///home/girotto/Área de Trabalho/TCC_Artefatos/tarefa_6_rasterizacao_cn/prints/validacao_raster.txt)
* **Produto Raster Final:** [resultado_ia_cn.tif](file:///home/girotto/Área de Trabalho/TCC_Artefatos/resultado_ia/resultado_ia_cn.tif) (3,26 MB)

---

## 4. O Que Foi Feito

1. **Gestão de Dependências no Ambiente Virtual (`.venv`):**
   - Identificou-se a ausência do pacote `rasterio` no ambiente virtual.
   - O agente executou a instalação dinâmica com segurança (`pip install rasterio`), preparando o ambiente para manipulação de dados matriciais sem intervenção do usuário.
2. **Definição Cartográfica Rigorosa da Matriz Raster:**
   - **Sistema de Coordenadas:** SIRGAS 2000 / Brazil Polyconic (`EPSG:5880`).
   - **Resolução Espacial:** $1000\text{ m} \times 1000\text{ m}$.
   - **Origem da Matriz:** Canto superior esquerdo em $(2.781.000\text{ m}, 10.587.000\text{ m})$.
   - **Extensão:** $X \in [2.781.000, 7.120.000]\text{ m}$; $Y \in [6.263.000, 10.587.000]\text{ m}$.
   - **Dimensões:** $4.339\text{ colunas} \times 4.324\text{ linhas}$ ($18.761.836\text{ células}$).
   - **Tipo e NoData:** `Float32` com NoData configurado em `-9999.0`.
   - **Amostragem Espacial:** Configuração de centróide de célula (`all_touched=False`), atribuindo a cada pixel estritamente o valor do polígono que contém seu centro.
3. **Engenharia de Memória e Processamento em Streaming:**
   - A matriz de 18,76 milhões de pontos foi pré-alocada em memória RAM consumindo apenas $71,57\text{ MB}$.
   - O processo de queima (*rasterize*) foi conduzido por streaming em 14 lotes de 100.000 feições lidas sob demanda via `pyogrio`, evitando sobrecarga de memória.
   - A taxa de rasterização atingiu **~12.000 feições/segundo**, completando todo o território nacional em **109,87 segundos**.
4. **Exportação Otimizada e Auditoria Técnica:**
   - O raster foi salvo como GeoTIFF ladrilhado (`tiled=True`, blocos de $256 \times 256$) com compressão DEFLATE sem perdas, resultando em um arquivo ultracompacto de apenas **3,26 MB**.
   - **Total de Células Válidas (Brasil):** 8.651.251 células ($\approx 8.651.251\text{ km}²$, em perfeita harmonia com a área territorial de ~8,515 milhões de km²).
   - **Estatísticas de CN:** Mínimo: 6.00, Máximo: 100.00, Média: 60.61, Mediana: 61.26, Desvio Padrão: 16.15.
