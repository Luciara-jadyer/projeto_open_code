# Projeto Data Pipeline Simplificado

## Objetivo
Pipeline de dados completo (do CSV à decisão) usando apenas Python + SQLite, sem infraestrutura complexa. Versão reduzida do projeto `data-engineering-roadmap` do Luciano Galvão.

---

## Arquitetura

```
CSV (dados brutos) 
    → Python (limpeza + transformação) 
    → SQLite (camadas Bronze → Silver → Gold) 
    → Streamlit Dashboard 
    → Script de Relatório
```

---

## Dados de Exemplo (2 fontes)

### 1. `data/vendas.csv` (100 linhas)

| Coluna | Tipo | Exemplo |
|--------|------|---------|
| id_venda | int | 1001 |
| data_venda | date | 2025-01-15 |
| id_cliente | int | 45 |
| id_produto | int | 301 |
| categoria | text | Eletrônicos |
| quantidade | int | 2 |
| preco_unitario | float | 150.00 |
| custo_unitario | float | 90.00 |

### 2. `data/clientes.csv` (50 linhas)

| Coluna | Tipo | Exemplo |
|--------|------|---------|
| id_cliente | int | 45 |
| nome | text | João Silva |
| estado | text | SP |
| data_cadastro | date | 2024-03-10 |
| email | text | joao@email.com |

---

## Pipeline (Python)

### Etapa 1: Bronze (dados crus)
- Ler CSV com `pandas`
- Salvar tabelas `bronze_vendas` e `bronze_clientes` no SQLite
- Sem transformações

### Etapa 2: Silver (dados limpos)
- Remover nulos e duplicatas
- Padronizar nomes de colunas (snake_case)
- Tipos corretos (datas, números)
- Salvar como `silver_vendas` e `silver_clientes`

### Etapa 3: Gold (dados agregados)
Três tabelas finais prontas para consumo:

```sql
-- gold_vendas_por_dia
SELECT data_venda, 
       SUM(receita) as receita_total,
       COUNT(DISTINCT id_cliente) as clientes_unicos,
       SUM(quantidade) as total_itens
FROM silver_vendas
GROUP BY data_venda
ORDER BY data_venda

-- gold_clientes_segmentacao
SELECT id_cliente, nome, estado,
       total_gasto,
       CASE 
           WHEN total_gasto > 5000 THEN 'VIP'
           WHEN total_gasto > 1000 THEN 'TOP_TIER'
           ELSE 'REGULAR'
       END as segmento
FROM silver_clientes

-- gold_produtos_desempenho
SELECT categoria,
       COUNT(*) as total_vendas,
       SUM(receita) as receita_total,
       AVG(preco_unitario) as preco_medio
FROM silver_vendas
GROUP BY categoria
```

---

## Produto 1: Dashboard (Streamlit)

### Página 1 - Visão Geral
- **KPIs**: Receita total, total de vendas, ticket médio, clientes ativos
- **Gráfico 1**: Receita por dia (linha)
- **Gráfico 2**: Vendas por categoria (barra)
- **Filtro**: Período (data inicial/final)

### Página 2 - Clientes
- **KPIs**: Total clientes, % VIP, % TOP_TIER
- **Gráfico 1**: Clientes por estado (barra horizontal)
- **Gráfico 2**: Top 10 clientes por gasto (barra)
- **Tabela**: Lista de clientes VIP

### Página 3 - Produtos
- **KPIs**: Total categorias, produto mais vendido
- **Gráfico 1**: Receita por categoria (pizza)
- **Gráfico 2**: Preço médio por categoria (barra)

Stack: `streamlit`, `plotly`, `pandas`, `sqlite3`

---

## Produto 2: Relatório Automático

Script Python que:
1. Conecta no SQLite
2. Consulta as tabelas Gold
3. Gera um resumo executivo em markdown
4. Salva em `relatorios/relatorio_YYYY-MM-DD.md`

### Estrutura do relatório:
```markdown
# Relatório Diário - YYYY-MM-DD

## Resumo
- Receita total: R$ XX.XXX
- Vendas realizadas: XX
- Ticket médio: R$ XX,XX

## Clientes
- Total: XX clientes ativos
- VIP: XX (XX%) | TOP_TIER: XX (XX%) | REGULAR: XX (XX%)

## Categorias
- Categoria com maior receita: XXXX (R$ XX.XXX)
- Categoria com maior volume: XXXX (XX vendas)
```

Stack: `pandas`, `sqlite3`

---

## Estrutura Final de Pastas

```
projeto_claude_code/
├── SPEC_SIMPLIFICADO.md      # Este documento
├── data/
│   ├── vendas.csv            # Dados brutos
│   └── clientes.csv          # Dados brutos
├── pipeline.py               # Script ETL (Bronze → Silver → Gold)
├── database.db               # SQLite (gerado pelo pipeline)
├── dashboard.py              # Streamlit app
├── relatorio.py              # Gerador de relatório
├── relatorios/               # Relatórios gerados
├── requirements.txt          # Dependências
└── .env                      # Config (se necessário)
```

---

## Como Executar

```bash
# 1. Instalar dependências
pip install pandas streamlit plotly

# 2. Gerar dados de exemplo + pipeline
python pipeline.py

# 3. Abrir dashboard
streamlit run dashboard.py

# 4. Gerar relatório
python relatorio.py
```

---

## Próximos Passos
1. [ ] Criar dados de exemplo (vendas.csv + clientes.csv)
2. [ ] Implementar pipeline.py (Bronze → Silver → Gold)
3. [ ] Implementar dashboard.py
4. [ ] Implementar relatorio.py
5. [ ] Testar o fluxo completo
