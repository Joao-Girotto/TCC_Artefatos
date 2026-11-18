# Plano de Implementação - Tarefa 5: Reprojeção Vetorial em Cascata e Conversão para GeoPackage

## 1. Visão Geral e Contexto
O objetivo desta tarefa é realizar a reprojeção cartográfica da Base Hidrográfica Otorgada da ANA (`BHO_2014_CN.shp`), contendo **1.305.955 polígonos** e **1.45 GB** de tamanho físico.

Conforme solicitado no prompt:
1. Verificar o CRS original do shapefile.
2. Identificado que o arquivo não está em SIRGAS 2000 (encontra-se em SAD 69 / EPSG:4618), reprojetá-lo primeiramente para **SIRGAS 2000 (EPSG:4674)** (sistema de coordenadas geográficas geodésicas oficial do Brasil).
3. Em seguida, reprojetá-lo para **SIRGAS 2000 / Brazil Polyconic (EPSG:5880)** (sistema de coordenadas métricas projetadas / projeção Policônica).
4. Gravar o resultado em `dados_processados/BHO_CN_5880.gpkg` em formato **GeoPackage (GPKG)**.
5. Garantir a preservação estrita de todas as 1.305.955 feições e todas as colunas de atributos.

---

## 2. Desafios Técnicos e Estratégia de Engenharia de Software

> [!IMPORTANT]
> **Gestão de Memória e Alta Performance (Big Vector Data):**
> O shapefile original possui 1.45 GB de geometrias vetoriais complexas. Carregar o arquivo completo de uma só vez para fazer múltiplas reprojeções pode gerar picos de memória excessivos.
>
> **Estratégia Adotada:**
> - Processamento em lotes (*chunks*) de 100.000 feições utilizando `pyogrio` e `geopandas`.
> - A cada lote, é feita a transformação de coordenadas em duas etapas (`to_crs(4674)` e `to_crs(5880)`).
> - As geometrias são salvas incrementalmente no GeoPackage com `append=True` e `promote_to_multi=True` (garantindo compatibilidade estrita com a especificação OGC GeoPackage).
> - O consumo de RAM permanecerá fixo e inferior a 150 MB durante toda a execução.

---

## 3. Mudanças Propostas

### Código e Estrutura de Pastas
- `tarefa_5_reprojecao_vetor/prompt.txt`: Registro do comando textual enviado pelo usuário.
- `tarefa_5_reprojecao_vetor/plano.md`: Este documento de planejamento.
- `tarefa_5_reprojecao_vetor/codigo/reprojetar_policonica.py`: Script Python estruturado para checagem de CRS, reprojeção em lote e exportação GPKG.
- `tarefa_5_reprojecao_vetor/prints/reprojecao_execucao.txt`: Registro completo da saída do terminal.
- `tarefa_5_reprojecao_vetor/prints/validacao_gpkg.txt`: Registro da auditoria e validação de integridade do arquivo GeoPackage gerado.
- `tarefa_5_reprojecao_vetor/walkthrough.md`: Relatório final documentando a metodologia, tempos de execução, consumo de tokens e custos.

---

## 4. Plano de Verificação

### Verificação Automatizada
1. **Execução do Script no `.venv`:**
   Rodar `reprojetar_policonica.py` dentro do ambiente virtual isolado `.venv`.
2. **Validação do Arquivo Gerado:**
   - Conferir se o arquivo `dados_processados/BHO_CN_5880.gpkg` foi criado e possui tamanho coerente.
   - Conferir se o CRS registrado no GeoPackage é `EPSG:5880`.
   - Conferir se o número total de feições é exatamente 1.305.955 (sem perda de feições).
   - Conferir se todas as 8 colunas de atributos originais foram preservadas com os mesmos tipos e valores.
   - Conferir as coordenadas métricas (Bounding Box em metros na projeção Policônica).
