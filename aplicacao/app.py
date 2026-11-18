#!/usr/bin/env python3
"""
Aplicação Streamlit - Tarefa 9: Exploração Espacial e Estatística de Curve Number (CN) do Brasil
Localização: aplicacao/app.py
"""

import os
import sys
import numpy as np
import pandas as pd
import pyogrio
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(
    page_title="Dashboard CN Brasil - Geoprocessamento Agêntico",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Caminhos base
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RASTER_PATH = os.path.join(BASE_DIR, "resultado_ia", "resultado_ia_cn.tif")
SHP_PATH = os.path.join(BASE_DIR, "dados_originais", "BHO_2014_CN.shp")
GPKG_PATH = os.path.join(BASE_DIR, "dados_processados", "BHO_CN_5880.gpkg")
PNG_PATH = os.path.join(BASE_DIR, "resultado_ia", "resultado_ia_cn.png")

# 2. Carregamento do Raster e Cálculo dos Indicadores Estatísticos Mandatórios
@st.cache_data(show_spinner="Carregando matriz raster e calculando estatísticas populacionais...")
def load_raster_data_and_indicators(tif_path, web_res=1200):
    if not os.path.exists(tif_path):
        raise FileNotFoundError(f"Arquivo raster não encontrado: {tif_path}")
        
    with rasterio.open(tif_path) as src:
        raw_band = src.read(1)
        nodata = src.nodata
        pixel_x, pixel_y = src.res
        
        # 1. Indicadores Estatísticos Oficiais do Raster Nacional
        valid_mask_full = raw_band != nodata
        valid_pixels = int(np.sum(valid_mask_full))
        area_km2 = float(valid_pixels * (pixel_x * pixel_y) / 1e6)
        
        valid_vals = raw_band[valid_mask_full]
        cn_min = float(np.min(valid_vals))
        cn_max = float(np.max(valid_vals))
        cn_mean = float(np.mean(valid_vals))
        # DESVIO-PADRÃO POPULACIONAL (ddof=0)
        cn_std_pop = float(np.std(valid_vals, ddof=0))
        
        indicators = {
            "valid_pixels": valid_pixels,
            "area_km2": area_km2,
            "min": cn_min,
            "max": cn_max,
            "mean": cn_mean,
            "std_pop": cn_std_pop
        }
        
        # 2. Reamostragem para WGS84 para exibição no Folium
        dst_crs = "EPSG:4326"
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds,
            dst_width=web_res, dst_height=web_res
        )
        dst_data = np.full((height, width), -9999.0, dtype=np.float32)
        reproject(
            source=rasterio.band(src, 1),
            destination=dst_data,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            dst_nodata=-9999.0,
            resampling=Resampling.nearest
        )
        bounds = rasterio.transform.array_bounds(height, width, transform)
        
    # Converter para RGBA com canal alfa transparente para NoData
    valid_mask_web = dst_data != -9999.0
    norm = mcolors.Normalize(vmin=0.0, vmax=100.0)
    cmap = plt.cm.viridis
    
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    colored = (cmap(norm(dst_data[valid_mask_web])) * 255).astype(np.uint8)
    rgba[valid_mask_web] = colored
    rgba[~valid_mask_web] = [0, 0, 0, 0]
    
    folium_bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
    
    return rgba, folium_bounds, indicators

@st.cache_data(show_spinner="Carregando tabela de atributos da Base Hidrográfica Otorgada...")
def load_table_sample(shp_path, limit=100000):
    df = pyogrio.read_dataframe(
        shp_path,
        columns=["COCURSODAG", "COBACIA", "Count", "Min_CN", "Max_CN", "Ave_CN", "StdDv_CN", "Var_CN"],
        max_features=limit,
        read_geometry=False
    )
    return df

# 3. Sidebar (Barra Lateral)
if os.path.exists(PNG_PATH):
    st.sidebar.image(PNG_PATH, caption="Visualização Cartográfica Nacional (EPSG:5880)")

st.sidebar.title("⚙️ Controles do Mapa")
map_style = st.sidebar.selectbox(
    "Estilo da Camada Base:",
    ["CartoDB positron", "OpenStreetMap", "CartoDB dark_matter"]
)

raster_opacity = st.sidebar.slider(
    "Opacidade do Raster:",
    min_value=0.1, max_value=1.0, value=0.85, step=0.05
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Especificação do Produto (Tarefa 9)")
st.sidebar.markdown("""
- **Vetor Base:** `dados_processados/BHO_CN_5880.gpkg`
- **Raster GeoTIFF:** `resultado_ia/resultado_ia_cn.tif`
- **Sistema de Coordenadas:** SIRGAS 2000 / Brazil Polyconic (`EPSG:5880`)
- **Resolução da Grade:** 1000 m × 1000 m (1 km²)
- **Origem do Grid:** Canto superior esquerdo $(2.781.000, 10.587.000)$
- **Extensão:** $4.339 \text{ colunas} \times 4.324 \text{ linhas}$
- **Tipo / NoData:** Float32 / NoData = -9999.0
""")

# 4. Cabeçalho Principal
st.title("🗺️ Painel Hidrológico Interativo: Curva Número (CN) do Brasil")
st.markdown("""
Aplicação analítica gerada de forma autônoma para exploração do raster nacional de **Curva Número (CN)**, 
reprojetado e processado a partir da **Base Hidrográfica Otorgada (BHO 2014)** da Agência Nacional de Águas (ANA).
""")

# Carregar dados
try:
    rgba_img, folium_bounds, indicators = load_raster_data_and_indicators(RASTER_PATH)
    attr_df = load_table_sample(SHP_PATH)
except Exception as e:
    st.error(f"Erro ao inicializar dados: {e}")
    st.stop()

# 5. Indicadores Estatísticos Exigidos pelo Usuário (Destaque Principal)
st.subheader("📊 Indicadores Estatísticos Mandatórios da Camada Raster")
c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric(
    label="Pixels Válidos",
    value=f"{indicators['valid_pixels']:,}",
    help="Quantidade total de células que contêm valores de CN dentro dos polígonos da hidrografia nacional."
)

c2.metric(
    label="Área Mapeada",
    value=f"{indicators['area_km2']:,.0f} km²",
    help="Área total territorial coberta pelo raster (cada pixel = 1 km²)."
)

c3.metric(
    label="Mínimo de CN",
    value=f"{indicators['min']:.2f}",
    help="Menor valor de CN registrado (solos com máxima infiltração de água e menor escoamento)."
)

c4.metric(
    label="Máximo de CN",
    value=f"{indicators['max']:.2f}",
    help="Maior valor de CN registrado (superfícies impermeáveis ou rochosas com maior escoamento)."
)

c5.metric(
    label="Média de CN",
    value=f"{indicators['mean']:.2f}",
    help="Média aritmética ponderada do Curve Number no território brasileiro."
)

c6.metric(
    label="Desvio-Padrão Pop.",
    value=f"{indicators['std_pop']:.2f}",
    help="Desvio-padrão populacional (σ com ddof=0) representando a dispersão global do CN."
)

st.markdown("---")

# 6. Abas de Conteúdo
tab_mapa, tab_stats, tab_dados = st.tabs([
    "🗺️ Mapa Interativo com Zoom",
    "📈 Análise Estatística e Distribuição",
    "📋 Tabela de Atributos da ANA"
])

# ----------------- ABA 1: MAPA INTERATIVO -----------------
with tab_mapa:
    st.subheader("Mapa Espacial da Curva Número (CN) no Brasil")
    st.caption("Navegue com zoom e pan para inspecionar o raster em nível de bacia e microbacia hidrográfica.")
    
    m = folium.Map(
        location=[-14.235, -51.925],
        zoom_start=4,
        tiles=map_style,
        control_scale=True
    )
    
    plugins.Fullscreen(position="topleft").add_to(m)
    plugins.MiniMap(toggle_display=True, position="bottomright").add_to(m)
    
    folium.raster_layers.ImageOverlay(
        image=rgba_img,
        bounds=folium_bounds,
        opacity=raster_opacity,
        name="Curva Número (CN) - 1000m",
        interactive=True,
        cross_origin=False,
        zindex=1
    ).add_to(m)
    
    folium.LayerControl(position="topright").add_to(m)
    
    st_folium(m, width="100%", height=600)
    st.info("ℹ️ **Escala Viridis:** Cores escuras/violeta representam menores valores de CN (alta capacidade de infiltração). Cores claras/amarelas representam valores elevados de CN (maior potencial de escoamento superficial).")

# ----------------- ABA 2: ANÁLISE ESTATÍSTICA -----------------
with tab_stats:
    st.subheader("Distribuição Estatística dos Valores de CN")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_hist = px.histogram(
            attr_df,
            x="Ave_CN",
            nbins=50,
            title="Histograma de Frequências da Curva Número (Ave_CN)",
            labels={"Ave_CN": "Curva Número Média (Ave_CN)", "count": "Contagem de Microbacias"},
            color_discrete_sequence=["#1b4f72"]
        )
        fig_hist.add_vline(x=indicators["mean"], line_dash="dash", line_color="red", annotation_text=f"Média: {indicators['mean']:.2f}")
        fig_hist.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with col_g2:
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(y=attr_df["Min_CN"], name="Mínimo (Min_CN)", marker_color="#2874a6"))
        fig_box.add_trace(go.Box(y=attr_df["Ave_CN"], name="Médio (Ave_CN)", marker_color="#239b56"))
        fig_box.add_trace(go.Box(y=attr_df["Max_CN"], name="Máximo (Max_CN)", marker_color="#b03a2e"))
        fig_box.update_layout(
            title="Diagrama de Caixa (Boxplot) de CN Mínimo, Médio e Máximo",
            yaxis_title="Curva Número (CN)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
    col_g3, col_g4 = st.columns(2)
    with col_g3:
        fig_scatter = px.scatter(
            attr_df.sample(min(25000, len(attr_df))),
            x="Count",
            y="StdDv_CN",
            color="Ave_CN",
            title="Dispersão: Desvio Padrão Interno vs Contagem de Células",
            labels={"Count": "Área em Pixels (Count)", "StdDv_CN": "Desvio Padrão Local", "Ave_CN": "Ave_CN"},
            color_continuous_scale="Viridis",
            opacity=0.6
        )
        fig_scatter.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_g4:
        corr_matrix = attr_df[["Count", "Min_CN", "Max_CN", "Ave_CN", "StdDv_CN", "Var_CN"]].corr()
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Matriz de Correlação Linear das Variáveis da BHO 2014"
        )
        fig_corr.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_corr, use_container_width=True)

# ----------------- ABA 3: TABELA DE ATRIBUTOS -----------------
with tab_dados:
    st.subheader("Amostra Tabular da Base Hidrográfica Otorgada")
    st.caption(f"Visualizando amostra representativa de {len(attr_df):,} feições originais da ANA.")
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        range_cn = st.slider("Filtrar por Intervalo de Ave_CN:", 0.0, 100.0, (15.0, 85.0))
    with col_f2:
        sort_col = st.selectbox("Ordenar Tabela por:", ["Ave_CN", "Count", "StdDv_CN", "Min_CN", "Max_CN"])
        
    filtered = attr_df[
        (attr_df["Ave_CN"] >= range_cn[0]) & (attr_df["Ave_CN"] <= range_cn[1])
    ].sort_values(by=sort_col, ascending=False)
    
    st.dataframe(filtered.head(1000), use_container_width=True, height=400)
    st.download_button(
        label="📥 Exportar Amostra Filtrada em CSV",
        data=filtered.head(5000).to_csv(index=False).encode("utf-8"),
        file_name="bho_cn_amostra_filtrada.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>TCC Engenharia Agêntica no Geoprocessamento | Google Antigravity</div>", unsafe_allow_html=True)
