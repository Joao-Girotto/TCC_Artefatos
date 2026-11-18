#!/usr/bin/env python3
"""
Tarefa 6: Rasterização Espacial de Polígonos de Curve Number (CN) para GeoTIFF
Entrada: dados_processados/BHO_CN_5880.gpkg (camada BHO_CN_5880, campo Ave_CN)
Saída:   resultado_ia/resultado_ia_cn.tif (EPSG:5880, 1000m, 4339x4324, Float32, NoData -9999)
"""

import os
import sys
import time
import numpy as np
import pyogrio
import rasterio
from rasterio import features
from rasterio.transform import from_origin

def main():
    start_total_time = time.time()
    
    # 1. Definição de caminhos e parâmetros do produto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    input_path = os.path.join(base_dir, "dados_processados", "BHO_CN_5880.gpkg")
    layer_name = "BHO_CN_5880"
    output_dir = os.path.join(base_dir, "resultado_ia")
    output_path = os.path.join(output_dir, "resultado_ia_cn.tif")
    
    # Especificação cartográfica estrita do produto
    crs_target = "EPSG:5880"
    x_min, x_max = 2781000.0, 7120000.0
    y_min, y_max = 6263000.0, 10587000.0
    pixel_size = 1000.0  # metros
    nodata_value = -9999.0
    
    width = int(round((x_max - x_min) / pixel_size))    # 4339 colunas
    height = int(round((y_max - y_min) / pixel_size))   # 4324 linhas
    transform = from_origin(x_min, y_max, pixel_size, pixel_size)
    
    print("=" * 80)
    print("    TAREFA 6: RASTERIZAÇÃO ESPACIAL DE CURVE NUMBER (CN) PARA GEOTIFF")
    print("=" * 80)
    print(f"[*] Vetor de Entrada:        {input_path} (layer: {layer_name})")
    print(f"[*] Raster de Saída:         {output_path}")
    print(f"[*] Sistema de Referência:   {crs_target} (SIRGAS 2000 / Brazil Polyconic)")
    print(f"[*] Resolução Espacial:      {pixel_size:.0f} m x {pixel_size:.0f} m")
    print(f"[*] Extensão X:              {x_min:,.0f} a {x_max:,.0f} m (Largura: {x_max - x_min:,.0f} m)")
    print(f"[*] Extensão Y:              {y_min:,.0f} a {y_max:,.0f} m (Altura:  {y_max - y_min:,.0f} m)")
    print(f"[*] Dimensões da Matriz:     {width} colunas x {height} linhas ({width * height:,} pixels)")
    print(f"[*] Tipo de Dado:            Float32 (NoData: {nodata_value})")
    print(f"[*] Critério de Amostragem:  Centro do Pixel (all_touched=False)")
    print("-" * 80)
    
    if not os.path.exists(input_path):
        print(f"[ERRO] Arquivo de entrada não encontrado: {input_path}")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    if os.path.exists(output_path):
        os.remove(output_path)
        print("[*] Raster anterior removido para garantir geração limpa.")

    # 2. Leitura de Metadados do GPKG
    print("\n[*] Passo 1: Lendo metadados da camada vetorial...")
    info_vector = pyogrio.read_info(input_path, layer=layer_name)
    total_features = info_vector["features"]
    print(f"    - Total de Feições Vetoriais: {total_features:,}")
    print(f"    - CRS da Camada:              {info_vector['crs']}")
    print(f"    - Campos disponíveis:         {list(info_vector['fields'])}")
    
    if "Ave_CN" not in info_vector["fields"]:
        print("[ERRO] Campo 'Ave_CN' não encontrado no arquivo vetorial!")
        sys.exit(1)

    # 3. Alocação da Matriz de Destino
    print("\n[*] Passo 2: Alocando matriz matricial na memória RAM...")
    t_alloc_start = time.time()
    raster_matrix = np.full((height, width), fill_value=nodata_value, dtype=np.float32)
    ram_mb = raster_matrix.nbytes / (1024 * 1024)
    print(f"    - Matriz alocada com sucesso em {time.time() - t_alloc_start:.3f}s (Consumo de RAM: {ram_mb:.2f} MB).")

    # 4. Rasterização em Streaming por Lotes (In-place Burn)
    chunk_size = 100000
    total_chunks = (total_features + chunk_size - 1) // chunk_size
    print(f"\n[*] Passo 3: Queimando feições na matriz em {total_chunks} lotes de até {chunk_size:,}...")
    
    t_raster_start = time.time()
    features_burned = 0
    
    for i in range(total_chunks):
        t_chunk_start = time.time()
        offset = i * chunk_size
        current_limit = min(chunk_size, total_features - offset)
        
        # Leitura seletiva apenas das colunas Ave_CN e geometry
        chunk_df = pyogrio.read_dataframe(
            input_path,
            layer=layer_name,
            columns=["Ave_CN", "geometry"],
            skip_features=offset,
            max_features=current_limit
        )
        
        # Extração de geometrias e valores válidos
        shapes = [
            (geom, float(val))
            for geom, val in zip(chunk_df.geometry, chunk_df["Ave_CN"])
            if geom is not None and not np.isnan(val)
        ]
        
        # Queima in-place na matriz existente
        features.rasterize(
            shapes=shapes,
            out=raster_matrix,
            transform=transform,
            all_touched=False
        )
        
        features_burned += len(chunk_df)
        pct = (features_burned / total_features) * 100
        t_chunk_end = time.time()
        chunk_time = t_chunk_end - t_chunk_start
        elapsed_total = t_chunk_end - t_raster_start
        rate = features_burned / elapsed_total
        eta_sec = (total_features - features_burned) / rate if rate > 0 else 0
        
        print(f"    - Lote {i+1:02d}/{total_chunks:02d} | "
              f"Feições: {features_burned:9,}/{total_features:,} ({pct:5.1f}%) | "
              f"Tempo Lote: {chunk_time:5.2f}s | "
              f"Taxa: {rate:6.0f} feat/s | "
              f"ETA: {eta_sec:5.1f}s")
              
    t_raster_end = time.time()
    raster_duration = t_raster_end - t_raster_start
    print(f"\n[Sucesso] Rasterização concluída em {raster_duration:.2f} segundos!")

    # 5. Gravação em GeoTIFF
    print("\n[*] Passo 4: Gravando matriz raster no formato GeoTIFF...")
    t_write_start = time.time()
    
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": rasterio.float32,
        "crs": crs_target,
        "transform": transform,
        "nodata": nodata_value,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256
    }
    
    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(raster_matrix, 1)
        
    t_write_end = time.time()
    write_duration = t_write_end - t_write_start
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[Sucesso] Arquivo gravado em {write_duration:.2f}s | Tamanho em disco: {file_size_mb:.2f} MB")

    # 6. Auditoria e Validação Rigorosa do GeoTIFF
    print("\n" + "=" * 80)
    print("                    VALIDAÇÃO DE INTEGRIDADE DO GEOTIFF")
    print("=" * 80)
    
    with rasterio.open(output_path) as src:
        band_data = src.read(1)
        
        print(f"[*] Driver do Raster:       {src.driver}")
        print(f"[*] Dimensões:              {src.width} colunas x {src.height} linhas")
        print(f"[*] CRS Registrado:         {src.crs}")
        print(f"[*] Limites (Bounds):       {src.bounds}")
        print(f"[*] Resolução (Pixel):      dx={src.res[0]:.1f} m, dy={src.res[1]:.1f} m")
        print(f"[*] Tipo de Dados:          {src.dtypes[0]}")
        print(f"[*] Valor NoData:           {src.nodata}")
        
        # Validações estruturais
        assert src.width == 4339, f"Largura incorreta: {src.width} != 4339"
        assert src.height == 4324, f"Altura incorreta: {src.height} != 4324"
        assert src.crs.to_epsg() == 5880, f"CRS incorreto: {src.crs}"
        assert src.dtypes[0] == "float32", f"Tipo de dados incorreto: {src.dtypes[0]}"
        assert src.nodata == -9999.0, f"NoData incorreto: {src.nodata}"
        assert src.bounds.left == 2781000.0, f"Xmin incorreto: {src.bounds.left}"
        assert src.bounds.right == 7120000.0, f"Xmax incorreto: {src.bounds.right}"
        assert src.bounds.bottom == 6263000.0, f"Ymin incorreto: {src.bounds.bottom}"
        assert src.bounds.top == 10587000.0, f"Ymax incorreto: {src.bounds.top}"
        print("[✓] Validações Estruturais (Dimensões, CRS, Bounds, NoData): 100% CONFORME")

        # Estatísticas dos pixels
        valid_mask = band_data != src.nodata
        valid_count = int(np.sum(valid_mask))
        nodata_count = int(np.sum(~valid_mask))
        total_pixels = src.width * src.height
        pct_valid = (valid_count / total_pixels) * 100
        
        valid_values = band_data[valid_mask]
        min_val = float(np.min(valid_values)) if valid_count > 0 else None
        max_val = float(np.max(valid_values)) if valid_count > 0 else None
        mean_val = float(np.mean(valid_values)) if valid_count > 0 else None
        std_val = float(np.std(valid_values)) if valid_count > 0 else None
        
        print("\n[*] Estatísticas da Matriz Raster:")
        print(f"    - Total de Células:      {total_pixels:,}")
        print(f"    - Células Válidas (CN):  {valid_count:,} ({pct_valid:.2f}% do grid)")
        print(f"    - Células NoData:        {nodata_count:,} ({100 - pct_valid:.2f}% do grid)")
        print(f"    - Valor Mínimo de CN:    {min_val:.2f}")
        print(f"    - Valor Máximo de CN:    {max_val:.2f}")
        print(f"    - Média de CN no Brasil: {mean_val:.2f}")
        print(f"    - Desvio Padrão de CN:   {std_val:.2f}")

    total_time = time.time() - start_total_time
    print("\n" + "=" * 80)
    print(f"[CONCLUÍDO COM SUCESSO] Tempo Total de Execução: {total_time:.2f} segundos")
    print("=" * 80)

if __name__ == "__main__":
    main()
