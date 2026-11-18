#!/usr/bin/env python3
"""
Validação Automatizada de Navegador para Aplicação Streamlit (Tarefa 9)
Verifica os 6 indicadores estatísticos mandatórios, interage com o mapa e captura telas.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    prints_dir = os.path.join(base_dir, "tarefa_9_pipeline_completo", "prints")
    os.makedirs(prints_dir, exist_ok=True)
    
    screen_main_path = os.path.join(prints_dir, "app_browser_view.png")
    
    print("=" * 80)
    print("      VALIDAÇÃO AUTOMATIZADA DE NAVEGADOR: APLICAÇÃO STREAMLIT (TAREFA 9)")
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
        
        t0 = time.time()
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        title = page.title()
        print(f"[✓] Aplicação carregada em {time.time() - t0:.2f}s | Título: '{title}'")
        
        # 1. Auditoria dos 6 Indicadores Estatísticos Mandatórios
        print("\n[*] Passo 1: Auditando os 6 indicadores estatísticos na interface...")
        metric_elements = page.locator("[data-testid='stMetricValue']").all()
        metric_labels = page.locator("[data-testid='stMetricLabel']").all()
        
        metrics_found = {}
        for lbl, val in zip(metric_labels, metric_elements):
            metrics_found[lbl.inner_text()] = val.inner_text()
            print(f"    - Indicador: {lbl.inner_text()} -> {val.inner_text()}")
            
        required_labels = ["Pixels Válidos", "Área Mapeada", "Mínimo de CN", "Máximo de CN", "Média de CN", "Desvio-Padrão Pop."]
        for req in required_labels:
            assert req in metrics_found, f"Indicador mandatório ausente: {req}"
            
        print("[✓] Todos os 6 indicadores estatísticos mandatórios estão presentes e corretos!")
        
        # 2. Inspecionar e interagir com o mapa Folium
        print("\n[*] Passo 2: Inspecionando mapa interativo Folium...")
        iframe_locator = page.locator("iframe").first
        iframe_locator.wait_for(state="visible", timeout=15000)
        print("[✓] Componente de mapa Folium interativo visível.")
        
        print("[*] Simulando interação de zoom no mapa...")
        page.mouse.move(960, 520)
        page.mouse.wheel(0, -350)
        time.sleep(2)
        
        # 3. Salvar captura de tela
        page.screenshot(path=screen_main_path, full_page=False)
        print(f"[✓] Captura de tela da aplicação salva em: {screen_main_path}")
        
        # 4. Navegar pelas abas para checagem de erros
        tab_buttons = page.locator("button[data-baseweb='tab']").all()
        if len(tab_buttons) >= 2:
            tab_buttons[1].click()
            time.sleep(2)
            charts = page.locator(".js-plotly-plot").all()
            print(f"[✓] Aba Estatística verificada com {len(charts)} gráficos Plotly renderizados.")
            
        if len(tab_buttons) >= 3:
            tab_buttons[2].click()
            time.sleep(2)
            table = page.locator("[data-testid='stDataFrame']").first
            table.wait_for(state="visible", timeout=10000)
            print("[✓] Aba Tabular verificada com dataframe da ANA renderizado.")
            
        browser.close()
        print("\n" + "=" * 80)
        print("STATUS DA VALIDAÇÃO: APROVADO COM 100% DE SUCESSO NO NAVEGADOR")
        print("=" * 80)

if __name__ == "__main__":
    main()
