import sqlite3
import pandas as pd
from datetime import date
from pathlib import Path

DB_PATH = "database.db"
RELATORIOS_DIR = Path("relatorios")

def get_conn():
    return sqlite3.connect(DB_PATH)

def carregar_dados():
    conn = get_conn()
    df_vendas = pd.read_sql("SELECT * FROM gold_vendas_por_dia", conn)
    df_clientes = pd.read_sql("SELECT * FROM gold_clientes_segmentacao", conn)
    df_produtos = pd.read_sql("SELECT * FROM gold_produtos_desempenho", conn)
    conn.close()
    return df_vendas, df_clientes, df_produtos

def gerar_relatorio():
    hoje = date.today()
    df_vendas, df_clientes, df_produtos = carregar_dados()

    receita_total = df_vendas["receita_total"].sum()
    total_vendas = df_vendas["total_vendas"].sum()
    total_itens = df_vendas["total_itens"].sum()
    ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
    clientes_ativos = df_vendas["clientes_unicos"].sum()

    total_clientes = len(df_clientes)
    qtd_vip = len(df_clientes[df_clientes["segmento"] == "VIP"])
    qtd_top = len(df_clientes[df_clientes["segmento"] == "TOP_TIER"])
    qtd_regular = len(df_clientes[df_clientes["segmento"] == "REGULAR"])

    top_categoria = df_produtos.iloc[0]
    maior_vol_cat = df_produtos.sort_values("total_vendas", ascending=False).iloc[0]

    conteudo = f"""# Relatorio Diario - {hoje}

## Resumo Executivo

| Indicador | Valor |
|-----------|-------|
| Receita Total | R$ {receita_total:,.2f} |
| Total de Vendas | {int(total_vendas)} |
| Itens Vendidos | {int(total_itens)} |
| Ticket Medio | R$ {ticket_medio:,.2f} |
| Clientes Atendidos | {int(clientes_ativos)} |

## Clientes

| Indicador | Valor |
|-----------|-------|
| Total de Clientes | {total_clientes} |
| VIP | {qtd_vip} ({qtd_vip/total_clientes*100:.1f}%) |
| TOP_TIER | {qtd_top} ({qtd_top/total_clientes*100:.1f}%) |
| REGULAR | {qtd_regular} ({qtd_regular/total_clientes*100:.1f}%) |

## Desempenho por Categoria

| Categoria | Vendas | Receita | Preco Medio |
|-----------|--------|---------|-------------|
"""
    for _, row in df_produtos.iterrows():
        conteudo += f"| {row['categoria']} | {int(row['total_vendas'])} | R$ {row['receita_total']:,.2f} | R$ {row['preco_medio']:,.2f} |\n"

    conteudo += f"""
## Destaques

- **Categoria com maior receita:** {top_categoria['categoria']} (R$ {top_categoria['receita_total']:,.2f})
- **Categoria com mais vendas:** {maior_vol_cat['categoria']} ({int(maior_vol_cat['total_vendas'])} vendas)
- **Ticket medio geral:** R$ {ticket_medio:,.2f}
- **Clientes VIP:** {qtd_vip} ({qtd_vip/total_clientes*100:.1f}% da base)

---
*Relatorio gerado automaticamente em {hoje}*
"""

    RELATORIOS_DIR.mkdir(exist_ok=True)
    arquivo = RELATORIOS_DIR / f"relatorio_{hoje}.md"
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"Relatorio salvo em: {arquivo}")
    print(conteudo)

if __name__ == "__main__":
    gerar_relatorio()
