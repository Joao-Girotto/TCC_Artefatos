# Engenharia de Software Agêntica Aplicada ao Geoprocessamento

> **Repositório de Pesquisa e Desenvolvimento de Trabalho de Conclusão de Curso (TCC)**  
> **Autor:** João Girotto  
> **Ambiente Operacional:** Google Antigravity & Modelos de Linguagem de Larga Escala (Gemini)  
> **Tema Central:** Avaliação da autonomia, resiliência, capacidade de autocorreção (*self-correction*) e eficiência de agentes inteligentes no ciclo completo de engenharia de software para Ciência de Dados Espaciais e Geoinformática.

---

## 📌 Visão Geral do Projeto

Este projeto investiga empiricamente a viabilidade e o desempenho de **Sistemas Agênticos Autônomos** na execução de pipelines complexos de software e geoprocessamento em escala nacional. 

A pesquisa utiliza como caso de estudo prático a **Base Hidrográfica Otifimada (BHO 2014)** da **Agência Nacional de Águas e Saneamento Básico (ANA)**, contendo mais de **1,3 milhão de polígonos** de microbacias hidrográficas associadas ao parâmetro hidrológico de infiltração **Curva Número (Curve Number - CN / SCS-NRCS)**.

O agente de IA operou em terminal Linux de forma autônoma, recebendo instruções em linguagem natural de alto nível e assumindo a responsabilidade técnica integral por:
1. Resolução e isolamento de dependências (`virtualenv`, `pip`).
2. Ingestão e transformação geodésica em streaming de Big Data geoespacial (SAD 69 $\rightarrow$ SIRGAS 2000 $\rightarrow$ Brazil Polyconic `EPSG:5880`).
3. Diagnóstico e autocorreção em tempo de execução de metadados espaciais legados (*naive geometries* ESRI WKT).
4. Rasterização afim de alta performance com amostragem matemática estrita por centro de pixel (`all_touched=False`) em uma matriz de 18,76 milhões de células ($1000\text{ m} \times 1000\text{ m}$).
5. Produção cartográfica digital de alta resolução (300 DPI com canal alfa transparente para áreas NoData).
6. Desenvolvimento e homologação de uma aplicação web reativa interativa ([Streamlit](https://streamlit.io/) + [Folium](https://python-visualization.github.io/folium/)).
7. Garantia da qualidade de interface (*QA Testing*) via automação de navegador sem interface gráfica (*headless Playwright*).

---

## 🗺️ Indicadores Populacionais Obtidos (Brasil CN)

A partir da grade matricial regular de 1 km gerada pelo pipeline autônomo sobre o território brasileiro:

| Indicador Estatístico | Valor Calculado | Detalhes Técnicos |
|---|---|---|
| **Número de Pixels Válidos** | `8.651.251` | Células contidas no território nacional |
| **Área Mapeada** | `8.651.251,00 km²` | Grade métrica regular ($1000\text{ m} \times 1000\text{ m}$) |
| **Mínimo de CN** | `6,00` | Corpos d'água / solos de alta capacidade de infiltração |
| **Máximo de CN** | `100,00` | Superfícies impermeáveis / escoamento total |
| **Média Populacional de CN** | `60,61` | Média ponderada pela área |
| **Desvio-Padrão Populacional** | `16,15` | Cálculo populacional ($ddof=0$) |

---

## 📂 Estrutura do Repositório

O projeto segue uma arquitetura rigorosa de documentação agêntica e reproducibilidade:

```text
├── aplicacao/                              # Aplicação Web Interativa (Streamlit)
│   ├── app.py                              # Código reativo com mapa Folium e métricas estatísticas
│   └── requirements.txt                    # Dependências da aplicação
├── dados_originais/                        # Diretório de entrada dos dados brutos (BHO ANA)
│   └── .gitkeep                            # (Dados > 1.5 GB ignorados no Git por limite de cota)
├── dados_processados/                      # Camadas espaciais reprojetadas
│   └── .gitkeep                            # (BHO_CN_5880.gpkg gerado com 1.85 GB)
├── resultado_ia/                           # Produtos finais gerados pelo agente
│   ├── resultado_ia_cn.tif                 # Raster GeoTIFF (EPSG:5880, Float32, 1km, NoData -9999)
│   └── resultado_ia_cn.png                 # Mapa temático em alta resolução (300 DPI)
├── tarefa_1_calculadora_juros/             # Validação do fluxo agêntico e self-correction inicial
├── tarefa_2_todo_list/                     # Testes de interação com subagentes e navegador web
├── tarefa_5_reprojecao_vetor/              # Reprojeção vetorial em cascata e escrita OGC GeoPackage
├── tarefa_6_rasterizacao_cn/               # Rasterização afim com controle de memória e amostragem
├── tarefa_7_visualizacao_raster/           # Composição visual cartográfica e canal alfa transparente
├── tarefa_8_dashboard_interativo/          # Construção da aplicação web com mapas e gráficos analíticos
├── tarefa_9_pipeline_completo/             # Re-execução unificada do pipeline integrado de ponta a ponta
│   ├── codigo/
│   │   ├── pipeline_completo.py            # Script orquestrador autônomo end-to-end
│   │   └── test_aplicacao.py               # Automação de testes de aceitação em navegador (Playwright)
│   ├── prints/                             # Capturas de tela, logs de execução e validação
│   ├── plano.md                            # Plano detalhado de engenharia
│   ├── prompt.txt                          # Prompt original do usuário
│   └── walkthrough.md                      # Relatório técnico completo de execução e custos
├── requirements.txt                        # Lista consolidada de dependências do ambiente
├── TCC_Escrita.md                          # Registro contínuo das tarefas, métricas de tokens e notas teóricas
└── README.md                               # Apresentação do projeto e instruções de uso
```

Cada pasta de tarefa (`tarefa_X`) é autocontida e abriga:
- `prompt.txt`: O comando exato fornecido pelo usuário em linguagem natural.
- `plano.md`: O plano de ação estruturado traçado pelo agente antes da execução.
- `codigo/`: Scripts Python e arquivos de código-fonte desenvolvidos.
- `prints/`: Registros de terminal, logs do interpretador e capturas visuais de validação.
- `walkthrough.md`: Relatório de encerramento com métricas de tempo, contagem de tokens, custos financeiros de API e lições aprendidas.

---

## 🛠️ Tecnologias e Bibliotecas Utilizadas

- **Linguagem & Runtime:** Python 3.10+
- **Ciência de Dados Geoespaciais:**
  - `geopandas` & `shapely`: Manipulação geométrica vetorial.
  - `pyogrio`: Ingestão vetorial ultra-rápida em C/GDAL via streaming em lotes.
  - `rasterio`: Álgebra matricial, queima vetorial afim e escrita de GeoTIFF comprimido.
  - `pyproj`: Projeções cartográficas e conversões geodésicas (PROJ / EPSG).
- **Visualização Cartográfica e Gráfica:**
  - `matplotlib` & `pillow`: Renderização cartográfica em 300 DPI com transparência alfa.
  - `plotly`: Gráficos dinâmicos e histogramas analíticos.
- **Frontend & Web Mapping:**
  - `streamlit`: Framework reativo para aplicações de dados.
  - `folium` & `streamlit-folium`: Mapas interativos baseados em Leaflet.js com reprojeção dinâmica para EPSG:4326.
- **Qualidade e Testes de Software:**
  - `playwright`: Automação e asserções de testes funcionais no navegador Chrome (*headless*).

---

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar o Repositório
```bash
git clone https://github.com/Joao-Girotto/TCC_Artefatos.git
cd TCC_Artefatos
```

### 2. Configurar o Ambiente Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Executar o Aplicativo Web Streamlit
O resultado final da modelagem espacial já se encontra pré-gerado em `resultado_ia/resultado_ia_cn.tif`. Para iniciar a interface interativa:
```bash
streamlit run aplicacao/app.py
```
Acesse no navegador: `http://localhost:8501`.

### 4. Re-executar o Pipeline Completo de Dados (Opcional)
Caso queira reproduzir a ingestão vetorial a partir do Shapefile bruto da ANA:
1. Faça o download da base BHO 2014 CN e descompacte os arquivos (`.shp`, `.dbf`, `.shx`, `.prj`) em `dados_originais/`.
2. Execute o pipeline integrado:
```bash
python tarefa_9_pipeline_completo/codigo/pipeline_completo.py
```
O pipeline realizará a reprojeção, a rasterização e a validação técnica de forma sequencial e reportará os tempos de processamento.

---

## 📊 Metadados de Custos e Engenharia Agêntica

Durante os experimentos, foi mantida a contabilização contínua do consumo de contexto e custos financeiros nos modelos Gemini (precificação de referência: Gemini 3.8 Flash):

* **Tarefa 9 (Pipeline Completo):** 5,20 milhões de tokens processados | Custo: **\$0,133 USD** (~R\$ 0,76) | Duração do processamento computacional: **3,45 minutos**.
* **Autonomia e Autocorreção:** O sistema demonstrou 100% de taxa de conclusão sem necessidade de suporte humano externo, resolvendo de forma autônoma exceções de geometrias *naive*, incompatibilidade de drivers gráficos headless e otimizações de memória RAM sob arquivos de múltiplos gigabytes.

---

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos e de pesquisa científica sob a licença [MIT](LICENSE).
