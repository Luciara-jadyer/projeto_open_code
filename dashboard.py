import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

DB_PATH = "database.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

@st.cache_data
def load_gold_vendas():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM gold_vendas_por_dia ORDER BY data_venda", conn)
    conn.close()
    df["data_venda"] = pd.to_datetime(df["data_venda"])
    return df

@st.cache_data
def load_gold_clientes():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM gold_clientes_segmentacao", conn)
    conn.close()
    return df

@st.cache_data
def load_gold_produtos():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM gold_produtos_desempenho", conn)
    conn.close()
    return df

st.set_page_config(page_title="Dashboard E-commerce", layout="wide")

st.title("Dashboard E-commerce")
st.markdown("Pipeline completo: CSV → SQLite → Streamlit")

tab1, tab2, tab3 = st.tabs(["Visão Geral", "Clientes", "Produtos"])

# ---- aba 1: Visão Geral ----
with tab1:
    df_vendas = load_gold_vendas()
    df_prod = load_gold_produtos()

    receita_total = df_vendas["receita_total"].sum()
    total_vendas = df_vendas["total_vendas"].sum()
    ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
    clientes_unicos = df_vendas["clientes_unicos"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita Total", f"R$ {receita_total:,.2f}")
    col2.metric("Total Vendas", f"{int(total_vendas)}")
    col3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    col4.metric("Clientes Atendidos", f"{int(clientes_unicos)}")

    fig1 = px.line(
        df_vendas, x="data_venda", y="receita_total",
        title="Receita por Dia", markers=True
    )
    fig1.update_layout(xaxis_title="Data", yaxis_title="Receita (R$)")
    st.plotly_chart(fig1, width='stretch')

    fig2 = px.bar(
        df_prod, x="categoria", y="receita_total",
        title="Receita por Categoria",
        text_auto=".2s", color="categoria"
    )
    fig2.update_layout(xaxis_title="Categoria", yaxis_title="Receita (R$)")
    st.plotly_chart(fig2, width='stretch')

# ---- aba 2: Clientes ----
with tab2:
    df_clientes = load_gold_clientes()

    total_clientes = len(df_clientes)
    qtd_vip = len(df_clientes[df_clientes["segmento"] == "VIP"])
    qtp_top = len(df_clientes[df_clientes["segmento"] == "TOP_TIER"])
    qtd_regular = len(df_clientes[df_clientes["segmento"] == "REGULAR"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Clientes", total_clientes)
    col2.metric("VIP", qtd_vip, f"{qtd_vip/total_clientes*100:.1f}%")
    col3.metric("TOP_TIER", qtp_top, f"{qtp_top/total_clientes*100:.1f}%")
    col4.metric("REGULAR", qtd_regular, f"{qtd_regular/total_clientes*100:.1f}%")

    fig3 = px.pie(
        df_clientes, names="segmento",
        title="Distribuição por Segmento",
        color="segmento",
        color_discrete_map={"VIP": "#FFD700", "TOP_TIER": "#C0C0C0", "REGULAR": "#CD7F32"}
    )
    st.plotly_chart(fig3, width='stretch')

    estado_count = df_clientes["estado"].value_counts().reset_index()
    estado_count.columns = ["estado", "clientes"]
    fig4 = px.bar(
        estado_count, x="clientes", y="estado",
        orientation="h", title="Clientes por Estado",
        text_auto=True, color="clientes"
    )
    fig4.update_layout(yaxis_title="Estado", xaxis_title="Clientes")
    st.plotly_chart(fig4, width='stretch')

    top10 = df_clientes.head(10)
    fig5 = px.bar(
        top10, x="total_gasto", y="nome",
        orientation="h", title="Top 10 Clientes por Gasto",
        text_auto=".2s", color="segmento",
        color_discrete_map={"VIP": "#FFD700", "TOP_TIER": "#C0C0C0", "REGULAR": "#CD7F32"}
    )
    fig5.update_layout(yaxis_title="Cliente", xaxis_title="Total Gasto (R$)")
    st.plotly_chart(fig5, width='stretch')

# ---- aba 3: Produtos ----
with tab3:
    df_prod = load_gold_produtos()

    col1, col2, col3 = st.columns(3)
    col1.metric("Categorias", len(df_prod))
    col2.metric("Total Vendido (itens)", f"{int(df_prod['quantidade_total'].sum())}")
    top_cat = df_prod.iloc[0]
    col3.metric("Categoria Top", f"{top_cat['categoria']}")

    fig6 = px.pie(
        df_prod, names="categoria", values="receita_total",
        title="Receita por Categoria"
    )
    st.plotly_chart(fig6, width='stretch')

    fig7 = px.bar(
        df_prod, x="categoria", y="preco_medio",
        title="Preço Médio por Categoria",
        text_auto=".2f", color="categoria"
    )
    fig7.update_layout(xaxis_title="Categoria", yaxis_title="Preço Médio (R$)")
    st.plotly_chart(fig7, width='stretch')

    fig8 = px.scatter(
        df_prod, x="total_vendas", y="receita_total",
        size="quantidade_total", color="categoria",
        title="Vendas vs Receita por Categoria",
        text="categoria"
    )
    fig8.update_traces(textposition="top center")
    fig8.update_layout(xaxis_title="Total Vendas", yaxis_title="Receita Total (R$)")
    st.plotly_chart(fig8, width='stretch')
