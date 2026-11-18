#!/usr/bin/env python3
"""
Dashboard Interativo Streamlit - Tarefa 8: Visualização de Raster GeoTIFF e Análise da Base ANA
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
    page_title="Dashboard CN Brasil - ANA & Geoprocessamento Agêntico",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Caminhos base
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RASTER_PATH = os.path.join(BASE_DIR, "resultado_ia", "resultado_ia_cn.tif")
SHP_PATH = os.path.join(BASE_DIR, "dados_originais", "BHO_2014_CN.shp")
PNG_PATH = os.path.join(BASE_DIR, "resultado_ia", "resultado_ia_cn.png")

# 2. Funções de Carregamento com Cache
@st.cache_data(show_spinner="Carregando e reamostrando raster para o mapa web...")
def load_raster_for_web(tif_path, target_resolution=1200):
    """
    Lê o GeoTIFF (EPSG:5880), reamostra com alta performance para WGS84 (EPSG:4326)
    e gera uma matriz RGBA compatível com camadas interativas do Folium.
    """
    with rasterio.open(tif_path) as src:
        dst_crs = "EPSG:4326"
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds,
            dst_width=target_resolution, dst_height=target_resolution
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
        # bounds: (west, south, east, north)
        
    # Converter para RGBA com canal alfa transparente para NoData
    valid_mask = dst_data != -9999.0
    norm = mcolors.Normalize(vmin=0.0, vmax=100.0)
    cmap = plt.cm.viridis
    
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    # Apenas células válidas recebem cor
    colored = (cmap(norm(dst_data[valid_mask])) * 255).astype(np.uint8)
    rgba[valid_mask] = colored
    rgba[~valid_mask] = [0, 0, 0, 0]
    
    # bounds para o Folium: [[south, west], [north, east]]
    folium_bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
    
    stats = {
        "valid_pixels": int(np.sum(valid_mask)),
        "min": float(np.min(dst_data[valid_mask])),
        "max": float(np.max(dst_data[valid_mask])),
        "mean": float(np.mean(dst_data[valid_mask])),
        "std": float(np.std(dst_data[valid_mask]))
    }
    
    return rgba, folium_bounds, stats

@st.cache_data(show_spinner="Carregando base de atributos do Shapefile da ANA...")
def load_shapefile_attributes(shp_path, sample_size=100000):
    """
    Carrega os dados tabulares da Base Hidrográfica Otorgada sem geometria para alta velocidade.
    """
    # Lê as primeiras 100k linhas para estatísticas e exploração fluida
    df = pyogrio.read_dataframe(
        shp_path,
        columns=["COCURSODAG", "COBACIA", "Count", "Min_CN", "Max_CN", "Ave_CN", "StdDv_CN", "Var_CN"],
        max_features=sample_size,
        read_geometry=False
    )
    return df

# 3. Barra Lateral (Sidebar)
st.sidebar.image(PNG_PATH if os.path.exists(PNG_PATH) else None, caption="Visão Panorâmica do CN no Brasil")
st.sidebar.title("Configurações do Mapa")

map_style = st.sidebar.selectbox(
    "Estilo do Mapa Base (TileLayer):",
    ["CartoDB positron", "OpenStreetMap", "CartoDB dark_matter"]
)

raster_opacity = st.sidebar.slider(
    "Opacidade da Camada Raster:",
    min_value=0.1, max_value=1.0, value=0.85, step=0.05
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ Metadados do Projeto")
st.sidebar.markdown("""
- **Fonte dos Dados:** Agência Nacional de Águas (ANA)
- **Base Vetorial:** BHO 2014 CN (1.305.955 polígonos)
- **Sistema de Origem:** SAD 69 (EPSG:4618)
- **Sistema Intermediário:** SIRGAS 2000 (EPSG:4674)
- **Sistema Projetado Final:** SIRGAS 2000 / Brazil Polyconic (EPSG:5880)
- **Resolução Espacial do Raster:** 1000 m × 1000 m
""")

# 4. Cabeçalho Principal
st.title("🗺️ Dashboard Interativo: Curva Número (CN) do Brasil")
st.markdown("""
Esta aplicação interativa integra o raster matricial de **Curva Número (CN)** gerado pelo sistema agêntico com a base vetorial oficial de microbacias da **Agência Nacional de Águas e Saneamento Básico (ANA)**.
""")

# Carregamento de dados
try:
    rgba_img, folium_bounds, raster_stats = load_raster_for_web(RASTER_PATH)
    attr_df = load_shapefile_attributes(SHP_PATH)
except Exception as e:
    st.error(f"Erro ao carregar arquivos de dados: {e}")
    st.stop()

# 5. Cards de Métricas Principais
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Feições Vetoriais (ANA)", "1.305.955", "100% Preservadas")
col2.metric("Média de CN (Território)", f"{raster_stats['mean']:.2f}", "Escala 0 a 100")
col3.metric("CN Mínimo Registrado", f"{raster_stats['min']:.1f}", "Alta Infiltração")
col4.metric("CN Máximo Registrado", f"{raster_stats['max']:.1f}", "Baixa Infiltração")
col5.metric("Desvio Padrão (CN)", f"{raster_stats['std']:.2f}", "Variabilidade")

st.markdown("---")

# 6. Abas Principais da Aplicação
tab_mapa, tab_stats, tab_tabela = st.tabs([
    "🗺️ Mapa Interativo com Zoom",
    "📈 Análise Estatística da Base ANA",
    "📋 Tabela de Dados e Atributos"
])

# ----------------- ABA 1: MAPA INTERATIVO -----------------
with tab_mapa:
    st.subheader("Visualização Espacial Contínua do Raster CN")
    st.caption("Utilize o controle de zoom, pan e tela cheia para explorar a variabilidade do Curve Number em diferentes regiões do Brasil.")
    
    # Criar Mapa Folium
    m = folium.Map(
        location=[-14.235, -51.925],
        zoom_start=4,
        tiles=map_style,
        control_scale=True
    )
    
    # Adicionar Overlay da Imagem Raster
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
    
    # Renderizar mapa interativo
    st_folium(m, width="100%", height=600)
    
    st.info("💡 **Dica de Interpretação:** Tons escuros/roxos indicam baixo CN (solos permeáveis e vegetação densa com alta capacidade de retenção). Tons claros/amarelados indicam alto CN (solos pouco permeáveis, superfícies rochosas ou maior propensão a escoamento superficial).")

# ----------------- ABA 2: ANÁLISE ESTATÍSTICA -----------------
with tab_stats:
    st.subheader("Análise Estatística dos Atributos Originais da ANA")
    
    c1, c2 = st.columns(2)
    
    with c1:
        # Histograma de Ave_CN
        fig_hist = px.histogram(
            attr_df,
            x="Ave_CN",
            nbins=40,
            title="Distribuição de Frequência do Curve Number Médio (Ave_CN)",
            labels={"Ave_CN": "Curva Número Média (Ave_CN)", "count": "Contagem de Microbacias"},
            color_discrete_sequence=["#2b5c8f"]
        )
        fig_hist.add_vline(x=raster_stats['mean'], line_dash="dash", line_color="red", annotation_text=f"Média: {raster_stats['mean']:.2f}")
        fig_hist.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with c2:
        # Boxplot comparativo de Min, Ave e Max
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(y=attr_df["Min_CN"], name="CN Mínimo (Min_CN)", marker_color="#1f77b4"))
        fig_box.add_trace(go.Box(y=attr_df["Ave_CN"], name="CN Médio (Ave_CN)", marker_color="#2ca02c"))
        fig_box.add_trace(go.Box(y=attr_df["Max_CN"], name="CN Máximo (Max_CN)", marker_color="#d62728"))
        fig_box.update_layout(
            title="Dispersão de Valores Extremos e Médios de CN por Polígono",
            yaxis_title="Valor de Curva Número (CN)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
    c3, c4 = st.columns(2)
    with c3:
        # Relação entre Contagem de Células e Desvio Padrão
        fig_scatter = px.scatter(
            attr_df.sample(min(20000, len(attr_df))),
            x="Count",
            y="StdDv_CN",
            color="Ave_CN",
            title="Variabilidade Interna (StdDv_CN) vs Tamanho da Bacia (Count)",
            labels={"Count": "Área em Pixels (Count)", "StdDv_CN": "Desvio Padrão do CN", "Ave_CN": "Ave_CN"},
            color_continuous_scale="Viridis",
            opacity=0.6
        )
        fig_scatter.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with c4:
        # Matriz de Correlação
        corr = attr_df[["Count", "Min_CN", "Max_CN", "Ave_CN", "StdDv_CN", "Var_CN"]].corr()
        fig_corr = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Matriz de Correlação Linear de Pearson dos Atributos Hidrológicos"
        )
        fig_corr.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_corr, use_container_width=True)

# ----------------- ABA 3: TABELA DE DADOS -----------------
with tab_tabela:
    st.subheader("Explorador de Dados Tabulares da Base ANA")
    st.caption(f"Exibindo amostra de {len(attr_df):,} feições da Base Hidrográfica Otorgada para inspeção analítica.")
    
    col_filter, col_sort = st.columns([2, 1])
    with col_filter:
        cn_range = st.slider("Filtrar por Faixa de Ave_CN:", 0.0, 100.0, (10.0, 90.0))
    with col_sort:
        sort_by = st.selectbox("Ordenar por:", ["Ave_CN", "Count", "StdDv_CN", "Min_CN", "Max_CN"])
        
    filtered_df = attr_df[
        (attr_df["Ave_CN"] >= cn_range[0]) & (attr_df["Ave_CN"] <= cn_range[1])
    ].sort_values(by=sort_by, ascending=False)
    
    st.dataframe(filtered_df.head(1000), use_container_width=True, height=400)
    st.download_button(
        label="📥 Baixar Amostra Filtrada (CSV)",
        data=filtered_df.head(5000).to_csv(index=False).encode("utf-8"),
        file_name="amostra_bho_cn_filtrada.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("<div style='text-align: center; color: #777;'>Trabalho de Conclusão de Curso (TCC) - Engenharia de Software Agêntica & Geoprocessamento com Google Antigravity</div>", unsafe_allow_html=True)
