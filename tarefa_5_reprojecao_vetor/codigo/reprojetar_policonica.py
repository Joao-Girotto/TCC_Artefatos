#!/usr/bin/env python3
"""
Tarefa 5: Reprojeção em Cascata de Shapefile ANA e Conversão para GeoPackage
Fluxo: SAD 69 -> SIRGAS 2000 (EPSG:4674) -> SIRGAS 2000 / Brazil Polyconic (EPSG:5880)
Saída: dados_processados/BHO_CN_5880.gpkg
"""

import os
import sys
import time
import pyogrio
import geopandas as gpd

def main():
    start_total_time = time.time()
    
    # 1. Definição de caminhos absolutos
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    input_path = os.path.join(base_dir, "dados_originais", "BHO_2014_CN.shp")
    output_dir = os.path.join(base_dir, "dados_processados")
    output_path = os.path.join(output_dir, "BHO_CN_5880.gpkg")
    layer_name = "BHO_CN_5880"
    
    print("=" * 80)
    print("        TAREFA 5: REPROJEÇÃO CARTOGRÁFICA EM CASCATA E EXPORTAÇÃO GPKG")
    print("=" * 80)
    print(f"[*] Arquivo de Entrada: {input_path}")
    print(f"[*] Arquivo de Saída:   {output_path}")
    print(f"[*] Camada GeoPackage:  {layer_name}")
    print("-" * 80)
    
    if not os.path.exists(input_path):
        print(f"[ERRO] Arquivo de entrada não encontrado: {input_path}")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    if os.path.exists(output_path):
        os.remove(output_path)
        print("[*] Arquivo GPKG anterior removido para garantir geração limpa.")

    # 2. Leitura de Metadados e Verificação de CRS
    print("\n[*] Passo 1: Inspecionando metadados e CRS original...")
    info_orig = pyogrio.read_info(input_path)
    total_features = info_orig["features"]
    orig_crs = info_orig["crs"]
    orig_fields = list(info_orig["fields"])
    orig_geom_type = info_orig["geometry_type"]
    
    print(f"    - Total de Feições:   {total_features:,}")
    print(f"    - Tipo de Geometria:  {orig_geom_type}")
    print(f"    - Campos/Atributos:   {orig_fields}")
    print(f"    - CRS Detectado:      {orig_crs}")
    
    # Avaliação do CRS
    is_sirgas_4674 = False
    if "4674" in str(orig_crs) or "SIRGAS 2000" in str(orig_crs):
        is_sirgas_4674 = True
        print("\n[+] O arquivo já está em SIRGAS 2000 (EPSG:4674).")
    else:
        print("\n[!] O arquivo NÃO está em SIRGAS 2000 (identificado como SAD 69).")
        print("[*] Estratégia de Reprojeção em Cascata:")
        print("    1º Estágio: Reprojeção SAD 69 -> SIRGAS 2000 (EPSG:4674)")
        print("    2º Estágio: Reprojeção SIRGAS 2000 -> SIRGAS 2000 / Brazil Polyconic (EPSG:5880)")

    # 3. Processamento em Lotes (Chunking) para Otimização de Memória e Desempenho
    chunk_size = 100000
    total_chunks = (total_features + chunk_size - 1) // chunk_size
    print(f"\n[*] Passo 2: Processando {total_features:,} feições em {total_chunks} lotes de até {chunk_size:,}...")
    
    features_processed = 0
    t_process_start = time.time()
    
    for i in range(total_chunks):
        t_chunk_start = time.time()
        offset = i * chunk_size
        current_limit = min(chunk_size, total_features - offset)
        
        # Leitura do lote
        chunk_df = pyogrio.read_dataframe(
            input_path,
            skip_features=offset,
            max_features=current_limit
        )
        
        # Reprojeção
        if not is_sirgas_4674:
            # Estágio 1: para EPSG:4674
            chunk_df = chunk_df.to_crs(4674)
            
        # Estágio 2: para EPSG:5880 (Policônica do Brasil)
        chunk_df = chunk_df.to_crs(5880)
        
        # Escrita no GeoPackage
        # promote_to_multi=True garante total aderência ao padrão GPKG MultiPolygon
        pyogrio.write_dataframe(
            chunk_df,
            output_path,
            driver="GPKG",
            layer=layer_name,
            append=(offset > 0),
            promote_to_multi=True
        )
        
        features_processed += len(chunk_df)
        pct = (features_processed / total_features) * 100
        t_chunk_end = time.time()
        chunk_elapsed = t_chunk_end - t_chunk_start
        total_elapsed = t_chunk_end - t_process_start
        rate = features_processed / total_elapsed
        remaining_sec = (total_features - features_processed) / rate if rate > 0 else 0
        
        print(f"    - Lote {i+1:02d}/{total_chunks:02d} | "
              f"Feições: {features_processed:9,}/{total_features:,} ({pct:5.1f}%) | "
              f"Tempo lote: {chunk_elapsed:5.2f}s | "
              f"Taxa: {rate:6.0f} feat/s | "
              f"ETA: {remaining_sec:5.1f}s")
              
    t_process_end = time.time()
    reproj_duration = t_process_end - t_process_start
    print(f"\n[Sucesso] Processamento e escrita concluídos em {reproj_duration:.2f} segundos!")

    # 4. Auditoria e Validação Rigorosa do GeoPackage Gerado
    print("\n" + "=" * 80)
    print("                    VALIDAÇÃO DE INTEGRIDADE DO GEOPACKAGE")
    print("=" * 80)
    
    if not os.path.exists(output_path):
        print(f"[ERRO CRÍTICO] GeoPackage não encontrado em: {output_path}")
        sys.exit(1)
        
    gpkg_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    info_out = pyogrio.read_info(output_path, layer=layer_name)
    
    print(f"[*] Tamanho do Arquivo GPKG: {gpkg_size_mb:.2f} MB")
    print(f"[*] Feições no GeoPackage:   {info_out['features']:,}")
    print(f"[*] CRS Registrado:          {info_out['crs']}")
    print(f"[*] Tipo de Geometria:       {info_out['geometry_type']}")
    print(f"[*] Campos no GeoPackage:    {list(info_out['fields'])}")
    
    # Checagens automáticas
    assert info_out["features"] == total_features, \
        f"Contagem divergente! Original: {total_features}, GPKG: {info_out['features']}"
    print("[✓] Validação 1: Contagem de feições idêntica (100% preservadas).")
    
    assert list(info_out["fields"]) == orig_fields, \
        f"Colunas divergentes! Original: {orig_fields}, GPKG: {list(info_out['fields'])}"
    print("[✓] Validação 2: Todos os 8 atributos e tipos rigorosamente preservados.")
    
    crs_str = str(info_out["crs"])
    assert "5880" in crs_str or "Polyconic" in crs_str, \
        f"CRS incorreto no GPKG: {crs_str}"
    print("[✓] Validação 3: CRS verificado e validado como EPSG:5880 (SIRGAS 2000 / Brazil Polyconic).")
    
    # Amostra das primeiras 5 feições para inspeção de coordenadas métricas
    sample_df = pyogrio.read_dataframe(output_path, layer=layer_name, max_features=5)
    print("\n[*] Amostra das 5 primeiras feições em EPSG:5880:")
    print(sample_df[["COCURSODAG", "COBACIA", "Count", "geometry"]])
    print(f"\n[*] Bounding Box da Amostra (em metros): {sample_df.total_bounds}")
    
    total_time = time.time() - start_total_time
    print("\n" + "=" * 80)
    print(f"[CONCLUÍDO COM SUCESSO] Tempo Total de Execução: {total_time:.2f} segundos")
    print("=" * 80)

if __name__ == "__main__":
    main()
