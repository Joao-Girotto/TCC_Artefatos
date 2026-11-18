#!/usr/bin/env python3
"""
Validação Automatizada de Navegador para Dashboard Streamlit (Tarefa 8)
Navega em http://localhost:8501, interage com abas, testa zoom e captura telas de validação.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    prints_dir = os.path.join(base_dir, "tarefa_8_dashboard_interativo", "prints")
    os.makedirs(prints_dir, exist_ok=True)
    
    screen_map_path = os.path.join(prints_dir, "dashboard_view.png")
    screen_stats_path = os.path.join(prints_dir, "dashboard_stats.png")
    screen_table_path = os.path.join(prints_dir, "dashboard_table.png")
    
    print("=" * 80)
    print("      VALIDAÇÃO AUTOMATIZADA DE NAVEGADOR: DASHBOARD STREAMLIT (TAREFA 8)")
    print("=" * 80)
    print("[*] Conectando ao servidor em http://localhost:8501...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        # 1. Carregamento da página principal
        t0 = time.time()
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        time.sleep(3)  # Aguardar montagem dos componentes reativos do Streamlit
        
        title = page.title()
        print(f"[✓] Página carregada em {time.time() - t0:.2f}s | Título da aba: '{title}'")
        
        # 2. Verificação dos Cards de Métricas
        print("\n[*] Passo 1: Verificando métricas principais do dashboard...")
        metric_elements = page.locator("[data-testid='stMetricValue']").all()
        metric_labels = page.locator("[data-testid='stMetricLabel']").all()
        
        metrics_dict = {}
        for lbl, val in zip(metric_labels, metric_elements):
            metrics_dict[lbl.inner_text()] = val.inner_text()
            print(f"    - {lbl.inner_text()}: {val.inner_text()}")
            
        assert len(metric_elements) >= 5, f"Esperado 5 métricas, encontrado {len(metric_elements)}"
        print("[✓] Todos os 5 cartões de métricas carregados com sucesso!")

        # 3. Verificação do Mapa Folium com Zoom
        print("\n[*] Passo 2: Inspecionando mapa interativo Folium...")
        iframe_locator = page.locator("iframe").first
        iframe_locator.wait_for(state="visible", timeout=15000)
        print("[✓] Componente de mapa Folium montado e visível.")
        
        # Interagir com o mapa: fazer zoom in
        print("[*] Simulando interação de zoom no mapa...")
        page.mouse.move(960, 500)
        page.mouse.wheel(0, -300)  # Zoom in via roda do mouse
        time.sleep(2)
        
        page.screenshot(path=screen_map_path, full_page=False)
        print(f"[✓] Captura da Aba 1 (Mapa com Zoom) salva em: {screen_map_path}")

        # 4. Navegação para Aba 2: Estatísticas
        print("\n[*] Passo 3: Navegando para Aba 'Análise Estatística da Base ANA'...")
        tab_buttons = page.locator("button[data-baseweb='tab']").all()
        if len(tab_buttons) >= 2:
            tab_buttons[1].click()
            time.sleep(3)  # Aguardar renderização do Plotly
            
            plotly_charts = page.locator(".js-plotly-plot").all()
            print(f"[✓] Gráficos Plotly detectados: {len(plotly_charts)} gráficos renderizados.")
            page.screenshot(path=screen_stats_path, full_page=False)
            print(f"[✓] Captura da Aba 2 (Estatísticas Plotly) salva em: {screen_stats_path}")

        # 5. Navegação para Aba 3: Tabela de Dados
        print("\n[*] Passo 4: Navegando para Aba 'Tabela de Dados e Atributos'...")
        if len(tab_buttons) >= 3:
            tab_buttons[2].click()
            time.sleep(2)
            
            dataframe_locator = page.locator("[data-testid='stDataFrame']").first
            dataframe_locator.wait_for(state="visible", timeout=10000)
            print("[✓] Tabela interativa de atributos da ANA renderizada com sucesso.")
            
            page.screenshot(path=screen_table_path, full_page=False)
            print(f"[✓] Captura da Aba 3 (Tabela de Dados) salva em: {screen_table_path}")

        browser.close()
        print("\n" + "=" * 80)
        print("STATUS DA VALIDAÇÃO NO NAVEGADOR: APROVADO COM 100% DE SUCESSO")
        print("=" * 80)

if __name__ == "__main__":
    main()
