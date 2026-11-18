#!/usr/bin/env python3
import sys
import argparse
import os

def calcular_juros_compostos(capital_inicial, taxa_anual, anos):
    # Taxa em percentual para decimal (ex: 10% -> 0.10)
    taxa_decimal = taxa_anual / 100.0
    
    dados_evolucao = []
    saldo_atual = capital_inicial
    
    for ano in range(1, anos + 1):
        saldo_anterior = saldo_atual
        juros_do_ano = saldo_atual * taxa_decimal
        saldo_atual += juros_do_ano
        dados_evolucao.append({
            "ano": ano,
            "saldo_anterior": saldo_anterior,
            "juros": juros_do_ano,
            "saldo_atual": saldo_atual
        })
        
    return dados_evolucao, saldo_atual

def exibir_tabela(dados, capital_inicial, taxa_anual, anos):
    print("=" * 60)
    print("            CALCULADORA DE JUROS COMPOSTOS")
    print("=" * 60)
    print(f" Capital Inicial: R$ {capital_inicial:,.2f}")
    print(f" Taxa de Juros : {taxa_anual}% ao ano")
    print(f" Período        : {anos} anos")
    print("-" * 60)
    print(f" {'Ano':^5} | {'Saldo Inicial':^15} | {'Juros Gerados':^13} | {'Saldo Final':^15}")
    print("-" * 60)
    
    total_juros = 0.0
    for d in dados:
        print(f" {d['ano']:^5} | R$ {d['saldo_anterior']:11,.2f} | R$ {d['juros']:9,.2f} | R$ {d['saldo_atual']:11,.2f}")
        total_juros += d['juros']
        
    print("-" * 60)
    total_acumulado = capital_inicial + total_juros
    print(f" Total de Juros Ganhos: R$ {total_juros:,.2f}")
    print(f" Montante Final       : R$ {total_acumulado:,.2f}")
    print("=" * 60)

def gerar_grafico(dados, capital_inicial, taxa_anual, anos, output_path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[Aviso] Matplotlib não está instalado. Pulando a geração do gráfico.")
        return False

    anos_lista = [0] + [d['ano'] for d in dados]
    saldos_lista = [capital_inicial] + [d['saldo_atual'] for d in dados]
    
    plt.figure(figsize=(10, 6))
    plt.plot(anos_lista, saldos_lista, marker='o', color='#1f77b4', linewidth=2.5, label='Montante Acumulado')
    plt.bar(anos_lista[1:], [d['juros'] for d in dados], alpha=0.3, color='#2ca02c', label='Juros Anuais')
    
    plt.title(f'Evolução dos Juros Compostos\n(Capital: R$ {capital_inicial:,.2f} | Juros: {taxa_anual}% a.a.)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Anos', fontsize=12)
    plt.ylabel('Valor (R$)', fontsize=12)
    plt.xticks(anos_lista)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper left', fontsize=11)
    
    # Adicionar rótulos de valores em cima dos pontos do gráfico
    for i, saldo in enumerate(saldos_lista):
        plt.annotate(f"R$ {saldo:,.2f}", (anos_lista[i], saldos_lista[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, fontweight='semibold')
        
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"\n[Sucesso] Gráfico salvo em: {output_path}")
    return True

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_grafico = os.path.join(os.path.dirname(script_dir), "prints", "evolucao_juros.png")

    parser = argparse.ArgumentParser(description="Calcula juros compostos ano a ano.")
    parser.add_argument("--capital", type=float, default=1000.0, help="Capital inicial (padrão: 1000.0)")
    parser.add_argument("--taxa", type=float, default=10.0, help="Taxa de juros anual em % (padrão: 10.0)")
    parser.add_argument("--anos", type=int, default=5, help="Quantidade de anos (padrão: 5)")
    parser.add_argument("--grafico", type=str, default=default_grafico, help="Caminho para salvar o gráfico")
    
    args = parser.parse_args()
    
    dados, montante_final = calcular_juros_compostos(args.capital, args.taxa, args.anos)
    exibir_tabela(dados, args.capital, args.taxa, args.anos)
    gerar_grafico(dados, args.capital, args.taxa, args.anos, args.grafico)

if __name__ == "__main__":
    main()
