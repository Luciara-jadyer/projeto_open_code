import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = "database.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def etapa_bronze():
    print("[Bronze] Ingerindo dados crus...")
    df_vendas = pd.read_csv("data/vendas.csv")
    df_clientes = pd.read_csv("data/clientes.csv")
    conn = conectar()
    df_vendas.to_sql("bronze_vendas", conn, if_exists="replace", index=False)
    df_clientes.to_sql("bronze_clientes", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  bronze_vendas: {len(df_vendas)} linhas")
    print(f"  bronze_clientes: {len(df_clientes)} linhas")

def etapa_silver():
    print("[Silver] Limpando e padronizando dados...")
    conn = conectar()
    df_vendas = pd.read_sql("SELECT * FROM bronze_vendas", conn)
    df_clientes = pd.read_sql("SELECT * FROM bronze_clientes", conn)

    df_vendas = df_vendas.drop_duplicates().dropna()
    df_vendas.columns = [c.strip().lower().replace(" ", "_") for c in df_vendas.columns]
    df_vendas["data_venda"] = pd.to_datetime(df_vendas["data_venda"])
    df_vendas["receita"] = df_vendas["quantidade"] * df_vendas["preco_unitario"]

    df_clientes = df_clientes.drop_duplicates().dropna()
    df_clientes.columns = [c.strip().lower().replace(" ", "_") for c in df_clientes.columns]
    df_clientes["data_cadastro"] = pd.to_datetime(df_clientes["data_cadastro"])

    df_vendas.to_sql("silver_vendas", conn, if_exists="replace", index=False)
    df_clientes.to_sql("silver_clientes", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  silver_vendas: {len(df_vendas)} linhas")
    print(f"  silver_clientes: {len(df_clientes)} linhas")

def etapa_gold():
    print("[Gold] Criando tabelas agregadas...")
    conn = conectar()
    df_vendas = pd.read_sql("SELECT * FROM silver_vendas", conn)
    df_clientes = pd.read_sql("SELECT * FROM silver_clientes", conn)

    gold_vendas = (
        df_vendas.groupby("data_venda")
        .agg(
            receita_total=("receita", "sum"),
            total_vendas=("id_venda", "count"),
            clientes_unicos=("id_cliente", "nunique"),
            total_itens=("quantidade", "sum"),
            ticket_medio=("receita", "mean"),
        )
        .reset_index()
        .sort_values("data_venda")
    )
    gold_vendas.to_sql("gold_vendas_por_dia", conn, if_exists="replace", index=False)
    print(f"  gold_vendas_por_dia: {len(gold_vendas)} linhas")

    total_gasto_cliente = df_vendas.groupby("id_cliente")["receita"].sum().reset_index()
    total_gasto_cliente.columns = ["id_cliente", "total_gasto"]

    gold_clientes = df_clientes.merge(total_gasto_cliente, on="id_cliente", how="left")
    gold_clientes["total_gasto"] = gold_clientes["total_gasto"].fillna(0)

    def segmentar(valor):
        if valor > 5000:
            return "VIP"
        elif valor > 1000:
            return "TOP_TIER"
        else:
            return "REGULAR"

    gold_clientes["segmento"] = gold_clientes["total_gasto"].apply(segmentar)
    gold_clientes = gold_clientes.sort_values("total_gasto", ascending=False)
    gold_clientes.to_sql("gold_clientes_segmentacao", conn, if_exists="replace", index=False)
    print(f"  gold_clientes_segmentacao: {len(gold_clientes)} linhas")

    gold_produtos = (
        df_vendas.groupby("categoria")
        .agg(
            total_vendas=("id_venda", "count"),
            receita_total=("receita", "sum"),
            preco_medio=("preco_unitario", "mean"),
            quantidade_total=("quantidade", "sum"),
        )
        .reset_index()
        .sort_values("receita_total", ascending=False)
    )
    gold_produtos.to_sql("gold_produtos_desempenho", conn, if_exists="replace", index=False)
    print(f"  gold_produtos_desempenho: {len(gold_produtos)} linhas")

    conn.close()

def run():
    print("=" * 40)
    print("Pipeline de Dados - Bronze -> Silver -> Gold")
    print("=" * 40)
    etapa_bronze()
    etapa_silver()
    etapa_gold()
    print("=" * 40)
    print("Pipeline concluido com sucesso!")
    print("=" * 40)

if __name__ == "__main__":
    run()
