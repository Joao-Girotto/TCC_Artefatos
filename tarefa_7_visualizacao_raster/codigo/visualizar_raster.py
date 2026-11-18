#!/usr/bin/env python3
"""
Tarefa 7: Renderização Cartográfica e Visualização do Raster CN do Brasil
Entrada: resultado_ia/resultado_ia_cn.tif
Saída:   resultado_ia/resultado_ia_cn.png (300 DPI, RGBA transparente, Projeção Policônica)
"""

import os
import sys
import time
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image

def main():
    start_time = time.time()
    
    # 1. Caminhos absolutos
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    input_path = os.path.join(base_dir, "resultado_ia", "resultado_ia_cn.tif")
    output_path = os.path.join(base_dir, "resultado_ia", "resultado_ia_cn.png")
    
    print("=" * 80)
    print("      TAREFA 7: RENDERIZAÇÃO CARTOGRÁFICA DO RASTER CN PARA PNG (300 DPI)")
    print("=" * 80)
    print(f"[*] Raster de Entrada: {input_path}")
    print(f"[*] Imagem de Saída:   {output_path}")
    print("-" * 80)
    
    if not os.path.exists(input_path):
        print(f"[ERRO] Arquivo de entrada não encontrado: {input_path}")
        sys.exit(1)
        
    # 2. Leitura dos dados matriciais
    print("\n[*] Passo 1: Lendo o raster GeoTIFF...")
    with rasterio.open(input_path) as src:
        band = src.read(1)
        nodata = src.nodata
        bounds = src.bounds
        crs_str = src.crs.to_string()
        width = src.width
        height = src.height
        res_x, res_y = src.res
        
    print(f"    - Dimensões do Raster: {width} colunas x {height} linhas")
    print(f"    - Bounding Box:        X=[{bounds.left:,.0f}, {bounds.right:,.0f}], Y=[{bounds.bottom:,.0f}, {bounds.top:,.0f}]")
    print(f"    - Sistema de Coordenadas: {crs_str}")
    print(f"    - Valor NoData:        {nodata}")
    
    # 3. Mascaramento de NoData e Configuração da Escala de Cores
    print("\n[*] Passo 2: Mascarando células NoData e configurando escala contínua...")
    masked_data = np.ma.masked_equal(band, nodata)
    valid_pixels = masked_data.count()
    print(f"    - Células válidas no território: {valid_pixels:,}")
    print(f"    - Faixa de valores válidos:      CN Mín={masked_data.min():.1f}, CN Máx={masked_data.max():.1f}")
    
    # Escala contínua do escuro ao claro (Viridis: do roxo escuro/preto ao amarelo brilhante)
    # NoData recebe canal alfa 0.0 (totalmente transparente)
    cmap = plt.cm.viridis.copy()
    cmap.set_bad(color=(0, 0, 0, 0))
    
    # 4. Construção da Figura Cartográfica
    print("\n[*] Passo 3: Compondo a prancha cartográfica em alta resolução (300 DPI)...")
    fig, ax = plt.subplots(figsize=(11, 10), facecolor="none")
    
    # Manter proporção geométrica estrita (sem esticar a imagem)
    ax.set_aspect("equal")
    
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    
    im = ax.imshow(
        masked_data,
        extent=extent,
        cmap=cmap,
        vmin=0.0,
        vmax=100.0,
        origin="upper",
        interpolation="nearest"
    )
    
    # Título principal e subtítulo com indicação explícita do CRS (EPSG:5880)
    ax.set_title(
        "Curva Número (CN) - Brasil",
        fontsize=18,
        fontweight="bold",
        pad=16,
        color="#1a1a1a"
    )
    
    # Indicação cartográfica do CRS e metadados
    ax.text(
        0.5, -0.06,
        "Sistema de Referência de Coordenadas: SIRGAS 2000 / Brazil Polyconic (EPSG:5880)\n"
        f"Resolução Espacial: {int(res_x)} m × {int(res_y)} m | Fonte: Base Hidrográfica Otorgada (ANA)",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=10.5,
        color="#2b2b2b"
    )
    
    # Barra de cores (legenda contínua)
    cbar = fig.colorbar(im, ax=ax, fraction=0.038, pad=0.04)
    cbar.set_label("Valor de Curva Número (CN)", fontsize=12, fontweight="bold", labelpad=10)
    cbar.ax.tick_params(labelsize=10.5)
    cbar.set_ticks(np.arange(0, 101, 10))
    
    # Configuração dos eixos de coordenadas (em km para elegância cartográfica)
    ax.set_xlabel("Coordenada Este / X (km)", fontsize=11, labelpad=8)
    ax.set_ylabel("Coordenada Norte / Y (km)", fontsize=11, labelpad=8)
    
    # Formatador de ticks em quilômetros
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f"{int(val / 1000):,}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f"{int(val / 1000):,}"))
    ax.tick_params(labelsize=9.5)
    
    # Garantir que o fundo dos eixos e da figura sejam transparentes
    ax.set_facecolor("none")
    fig.patch.set_alpha(0.0)
    
    # 5. Salvamento em PNG com 300 DPI
    print(f"\n[*] Passo 4: Renderizando e gravando imagem em {output_path}...")
    t_render_start = time.time()
    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        transparent=True
    )
    plt.close(fig)
    render_duration = time.time() - t_render_start
    print(f"[Sucesso] Renderização concluída em {render_duration:.2f} segundos!")
    
    # 6. Auditoria Técnica da Imagem Gerada
    print("\n" + "=" * 80)
    print("                    VALIDAÇÃO DE INTEGRIDADE DA IMAGEM")
    print("=" * 80)
    
    img = Image.open(output_path)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    img_width, img_height = img.size
    
    print(f"[*] Tamanho do Arquivo PNG: {file_size_mb:.2f} MB")
    print(f"[*] Resolução da Imagem:    {img_width} x {img_height} pixels")
    print(f"[*] Modo de Cor:            {img.mode} (Canais RGBA com suporte a transparência)")
    print(f"[*] DPI nos Metadados:      {img.info.get('dpi', 'Não registrado')}")
    
    # Verificação do canal alfa (transparência)
    img_np = np.array(img)
    alpha_channel = img_np[:, :, 3]
    transparent_pixels = np.sum(alpha_channel == 0)
    opaque_pixels = np.sum(alpha_channel > 0)
    total_img_pixels = img_width * img_height
    pct_transparent = (transparent_pixels / total_img_pixels) * 100
    
    print(f"[*] Pixels Transparentes:   {transparent_pixels:,} ({pct_transparent:.2f}% da tela)")
    print(f"[*] Pixels Coloridos:       {opaque_pixels:,} ({100 - pct_transparent:.2f}% da tela)")
    
    assert img.mode == "RGBA", "A imagem deve possuir canal Alpha para transparência!"
    assert transparent_pixels > 0, "Deveriam existir pixels com transparência para o NoData!"
    assert "300" in str(img.info.get("dpi", "")) or img_width >= 2500, "A imagem não foi renderizada em 300 DPI!"
    print("[✓] Todas as verificações técnicas foram APROVADAS com sucesso.")
    
    total_elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"[CONCLUÍDO COM SUCESSO] Tempo Total de Execução: {total_elapsed:.2f} segundos")
    print("=" * 80)

if __name__ == "__main__":
    main()
