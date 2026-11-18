#!/usr/bin/env python3
"""
Tarefa 9: Pipeline Completo de Geoprocessamento de Ponta a Ponta
Etapa 1: Reprojeção em Cascata (SAD 69 -> SIRGAS 2000 -> Brazil Polyconic EPSG:5880) -> BHO_CN_5880.gpkg
Etapa 2: Rasterização Espacial de Ave_CN (1000m x 1000m, EPSG:5880) -> resultado_ia_cn.tif
Etapa 3: Geração de Cartografia em Alta Resolução (300 DPI, RGBA transparente) -> resultado_ia_cn.png
"""

import os
import sys
import time

# Configurar diretório de cache do Matplotlib em local gravável
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"

import numpy as np
import pyogrio
import rasterio
from rasterio import features
from rasterio.transform import from_origin
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image

def main():
    total_start = time.time()
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    shp_input = os.path.join(base_dir, "dados_originais", "BHO_2014_CN.shp")
    gpkg_output = os.path.join(base_dir, "dados_processados", "BHO_CN_5880.gpkg")
    tif_output = os.path.join(base_dir, "resultado_ia", "resultado_ia_cn.tif")
    png_output = os.path.join(base_dir, "resultado_ia", "resultado_ia_cn.png")
    
    print("=" * 80)
    print("        TAREFA 9: PIPELINE INTEGRADO DE GEOPROCESSAMENTO DE PONTA A PONTA")
    print("=" * 80)
    print(f"[*] Entrada Original (Shapefile): {shp_input}")
    print(f"[*] Saída Vetorial (GeoPackage):  {gpkg_output}")
    print(f"[*] Saída Raster (GeoTIFF):       {tif_output}")
    print(f"[*] Visualização Gráfica (PNG):   {png_output}")
    print("-" * 80)
    
    if not os.path.exists(shp_input):
        print(f"[ERRO CRÍTICO] Shapefile original não encontrado em {shp_input}")
        sys.exit(1)
        
    os.makedirs(os.path.dirname(gpkg_output), exist_ok=True)
    os.makedirs(os.path.dirname(tif_output), exist_ok=True)
    
    # =========================================================================
    # ETAPA 1: REPROJEÇÃO EM CASCATA PARA SIRGAS 2000 / BRAZIL POLYCONIC (5880)
    # =========================================================================
    print("\n>>> ETAPA 1: REPROJEÇÃO CARTOGRÁFICA DO SHAPEFILE BHO 2014 CN")
    if os.path.exists(gpkg_output):
        os.remove(gpkg_output)
        print("    [*] Arquivo GPKG anterior removido para execução limpa.")
        
    info_orig = pyogrio.read_info(shp_input)
    total_features = info_orig["features"]
    orig_crs = info_orig["crs"]
    orig_fields = list(info_orig["fields"])
    
    print(f"    - Feições a processar: {total_features:,}")
    print(f"    - CRS Original:        {orig_crs}")
    print(f"    - Campos de Atributo:  {orig_fields}")
    
    chunk_size = 100000
    total_chunks = (total_features + chunk_size - 1) // chunk_size
    t_reproj_start = time.time()
    features_reprojected = 0
    
    for i in range(total_chunks):
        t0 = time.time()
        offset = i * chunk_size
        limit = min(chunk_size, total_features - offset)
        
        chunk_df = pyogrio.read_dataframe(
            shp_input,
            skip_features=offset,
            max_features=limit
        )
        
        # Tratamento de CRS ingênuo (legacy ESRI SAD69 WKT sem autoridade EPSG declarada)
        if chunk_df.crs is None:
            chunk_df = chunk_df.set_crs(4618)
            
        # Cascata: SAD 69 (4618) -> SIRGAS 2000 (4674) -> Brazil Polyconic (5880)
        chunk_df = chunk_df.to_crs(4674).to_crs(5880)
        
        # Escrita com garantia de tipagem MultiPolygon
        pyogrio.write_dataframe(
            chunk_df,
            gpkg_output,
            driver="GPKG",
            layer="BHO_CN_5880",
            append=(offset > 0),
            promote_to_multi=True
        )
        
        features_reprojected += len(chunk_df)
        pct = (features_reprojected / total_features) * 100
        t1 = time.time()
        rate = features_reprojected / (t1 - t_reproj_start)
        print(f"    - [Vetor] Lote {i+1:02d}/{total_chunks:02d} | "
              f"Feições: {features_reprojected:9,}/{total_features:,} ({pct:5.1f}%) | "
              f"Tempo: {t1-t0:5.2f}s | Taxa: {rate:6.0f} feat/s")
              
    t_reproj_end = time.time()
    reproj_duration = t_reproj_end - t_reproj_start
    print(f"[✓] Etapa 1 Concluída em {reproj_duration:.2f}s! GPKG gerado com {os.path.getsize(gpkg_output)/(1024*1024):.2f} MB.")
    
    # =========================================================================
    # ETAPA 2: RASTERIZAÇÃO ESPACIAL DO CAMPO Ave_CN PARA GEOTIFF (EPSG:5880)
    # =========================================================================
    print("\n>>> ETAPA 2: RASTERIZAÇÃO DE CURVE NUMBER (Ave_CN) EM 1000m x 1000m")
    if os.path.exists(tif_output):
        os.remove(tif_output)
        print("    [*] Arquivo GeoTIFF anterior removido para execução limpa.")
        
    x_min, x_max = 2781000.0, 7120000.0
    y_min, y_max = 6263000.0, 10587000.0
    pixel_size = 1000.0
    nodata_val = -9999.0
    
    width = int(round((x_max - x_min) / pixel_size))    # 4339
    height = int(round((y_max - y_min) / pixel_size))   # 4324
    transform = from_origin(x_min, y_max, pixel_size, pixel_size)
    
    print(f"    - Grid Raster: {width} colunas x {height} linhas ({width * height:,} pixels)")
    print(f"    - Extensão: X=[{x_min:,.0f}, {x_max:,.0f}], Y=[{y_min:,.0f}, {y_max:,.0f}]")
    print(f"    - Resolução: {pixel_size:.0f}m | NoData: {nodata_val}")
    
    raster_matrix = np.full((height, width), fill_value=nodata_val, dtype=np.float32)
    t_raster_start = time.time()
    features_burned = 0
    
    for i in range(total_chunks):
        t0 = time.time()
        offset = i * chunk_size
        limit = min(chunk_size, total_features - offset)
        
        chunk_df = pyogrio.read_dataframe(
            gpkg_output,
            layer="BHO_CN_5880",
            columns=["Ave_CN", "geometry"],
            skip_features=offset,
            max_features=limit
        )
        
        shapes = [
            (geom, float(val))
            for geom, val in zip(chunk_df.geometry, chunk_df["Ave_CN"])
            if geom is not None and not np.isnan(val)
        ]
        
        features.rasterize(
            shapes=shapes,
            out=raster_matrix,
            transform=transform,
            all_touched=False
        )
        
        features_burned += len(chunk_df)
        pct = (features_burned / total_features) * 100
        t1 = time.time()
        rate = features_burned / (t1 - t_raster_start)
        print(f"    - [Raster] Lote {i+1:02d}/{total_chunks:02d} | "
              f"Feições: {features_burned:9,}/{total_features:,} ({pct:5.1f}%) | "
              f"Tempo: {t1-t0:5.2f}s | Taxa: {rate:6.0f} feat/s")
              
    t_raster_end = time.time()
    raster_duration = t_raster_end - t_raster_start
    print(f"[✓] Queima matricial concluída em {raster_duration:.2f}s!")
    
    # Gravação do GeoTIFF
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": rasterio.float32,
        "crs": "EPSG:5880",
        "transform": transform,
        "nodata": nodata_val,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256
    }
    
    with rasterio.open(tif_output, "w", **profile) as dst:
        dst.write(raster_matrix, 1)
    print(f"[✓] Arquivo GeoTIFF gravado com sucesso em {tif_output} ({os.path.getsize(tif_output)/(1024*1024):.2f} MB)")

    # =========================================================================
    # ETAPA 3: CÁLCULO DOS INDICADORES ESTATÍSTICOS POPULACIONAIS
    # =========================================================================
    print("\n>>> ETAPA 3: CÁLCULO E VALIDAÇÃO DOS INDICADORES ESTATÍSTICOS")
    valid_mask = raster_matrix != nodata_val
    valid_pixels = int(np.sum(valid_mask))
    area_km2 = float(valid_pixels * (pixel_size * pixel_size) / 1e6)
    
    valid_values = raster_matrix[valid_mask]
    cn_min = float(np.min(valid_values))
    cn_max = float(np.max(valid_values))
    cn_mean = float(np.mean(valid_values))
    # DESVIO-PADRÃO POPULACIONAL: ddof=0
    cn_std_pop = float(np.std(valid_values, ddof=0))
    
    print("    [INDICADORES ESTATÍSTICOS DO CURVE NUMBER NO BRASIL]")
    print(f"    1. Número de Pixels Válidos:      {valid_pixels:,}")
    print(f"    2. Área Coberta pelo Raster:       {area_km2:,.2f} km²")
    print(f"    3. Valor Mínimo de CN:             {cn_min:.2f}")
    print(f"    4. Valor Máximo de CN:             {cn_max:.2f}")
    print(f"    5. Média Populacional de CN:       {cn_mean:.2f}")
    print(f"    6. Desvio-Padrão Populacional CN:  {cn_std_pop:.2f}")

    # =========================================================================
    # ETAPA 4: GERAÇÃO DA PEÇA CARTOGRÁFICA DE VISUALIZAÇÃO (PNG 300 DPI)
    # =========================================================================
    print("\n>>> ETAPA 4: GERAÇÃO DA IMAGEM DE ALTA RESOLUÇÃO (PNG 300 DPI)")
    masked_data = np.ma.masked_equal(raster_matrix, nodata_val)
    cmap = plt.cm.viridis.copy()
    cmap.set_bad(color=(0, 0, 0, 0))
    
    fig, ax = plt.subplots(figsize=(11, 10), facecolor="none")
    ax.set_aspect("equal")
    extent = [x_min, x_max, y_min, y_max]
    
    im = ax.imshow(
        masked_data,
        extent=extent,
        cmap=cmap,
        vmin=0.0,
        vmax=100.0,
        origin="upper",
        interpolation="nearest"
    )
    
    ax.set_title("Curva Número (CN) - Brasil", fontsize=18, fontweight="bold", pad=16, color="#1a1a1a")
    ax.text(
        0.5, -0.06,
        "Sistema de Referência de Coordenadas: SIRGAS 2000 / Brazil Polyconic (EPSG:5880)\n"
        f"Pixels Válidos: {valid_pixels:,} ({area_km2:,.0f} km²) | Média CN: {cn_mean:.2f} | σ Populacional: {cn_std_pop:.2f}",
        transform=ax.transAxes, ha="center", va="top", fontsize=10.5, color="#2b2b2b"
    )
    
    cbar = fig.colorbar(im, ax=ax, fraction=0.038, pad=0.04)
    cbar.set_label("Valor de Curva Número (CN)", fontsize=12, fontweight="bold", labelpad=10)
    cbar.ax.tick_params(labelsize=10.5)
    cbar.set_ticks(np.arange(0, 101, 10))
    
    ax.set_xlabel("Coordenada Este / X (km)", fontsize=11, labelpad=8)
    ax.set_ylabel("Coordenada Norte / Y (km)", fontsize=11, labelpad=8)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{int(v / 1000):,}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{int(v / 1000):,}"))
    ax.set_facecolor("none")
    fig.patch.set_alpha(0.0)
    
    plt.savefig(png_output, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)
    print(f"[✓] Imagem PNG gravada com sucesso em {png_output} ({os.path.getsize(png_output)/(1024*1024):.2f} MB)")

    total_time = time.time() - total_start
    print("\n" + "=" * 80)
    print(f"[SUCESSO TOTAL] Pipeline Completo Executado em {total_time:.2f} segundos!")
    print("=" * 80)

if __name__ == "__main__":
    main()
