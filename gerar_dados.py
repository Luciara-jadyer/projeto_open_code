import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

# --- CLIENTES ---
nomes = [
    "João Silva", "Maria Santos", "Carlos Oliveira", "Ana Costa", "Pedro Souza",
    "Julia Lima", "Lucas Pereira", "Fernanda Almeida", "Rafael Barbosa", "Camila Rocha",
    "Gabriel Martins", "Larissa Gomes", "Felipe Ribeiro", "Isabela Carvalho", "Thiago Teixeira",
    "Amanda Rodrigues", "Bruno Alves", "Patricia Nunes", "Rodrigo Mendes", "Vanessa Dias",
    "Eduardo Moreira", "Tatiana Freitas", "Marcos Vieira", "Renata Cardoso", "Leandro Azevedo",
    "Carolina Farias", "Diego Campos", "Juliana Pinto", "Alexandre Assis", "Priscila Moura",
    "André Castro", "Bianca Tavares", "Ricardo Correia", "Daniele Peixoto", "Fábio Dantas",
    "Luciana Vargas", "Gustavo Rezende", "Aline Duarte", "Renato Figueiredo", "Sabrina Lopes",
    "Roberto Batista", "Cristiane Guimarães", "Marcelo Serpa", "Fabiana Melo", "Danilo Freitas",
    "Simone Branco", "Vinicius Paz", "Sandra Zago", "Nelson Chaves", "Elaine Ávila"
]
estados = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "PE", "CE", "ES"]

clientes = []
for i, nome in enumerate(nomes, start=1):
    estado = random.choice(estados)
    dias_cadastro = random.randint(30, 700)
    data_cadastro = datetime(2025, 1, 1) - timedelta(days=dias_cadastro)
    email = nome.lower().replace(" ", ".") + "@email.com"
    clientes.append({
        "id_cliente": i,
        "nome": nome,
        "estado": estado,
        "data_cadastro": data_cadastro.strftime("%Y-%m-%d"),
        "email": email
    })

df_clientes = pd.DataFrame(clientes)
df_clientes.to_csv("data/clientes.csv", index=False)
print(f"Clientes: {len(df_clientes)} registros criados")

# --- VENDAS ---
categorias_produtos = {
    "Eletrônicos": [(301, 150.00), (302, 89.90), (303, 2500.00), (304, 35.50), (305, 1299.99), (306, 450.00), (307, 89.00)],
    "Roupas": [(401, 79.90), (402, 149.90), (403, 39.90), (404, 199.90), (405, 59.90)],
    "Casa": [(501, 29.90), (502, 399.90), (503, 89.90), (504, 149.90), (505, 19.90)],
    "Alimentos": [(601, 12.90), (602, 25.00), (603, 45.00), (604, 8.90), (605, 32.00)],
    "Esportes": [(701, 199.90), (702, 89.90), (703, 59.90), (704, 299.90), (705, 129.90)]
}
custo_percentual = {"Eletrônicos": 0.6, "Roupas": 0.4, "Casa": 0.5, "Alimentos": 0.55, "Esportes": 0.45}

vendas = []
venda_id = 1001
data_inicio = datetime(2025, 1, 1)
data_fim = datetime(2025, 4, 30)

for _ in range(120):
    cliente_id = random.randint(1, 50)
    categoria = random.choice(list(categorias_produtos.keys()))
    produtos = categorias_produtos[categoria]
    produto_id, preco = random.choice(produtos)
    qtd = random.randint(1, 5)
    custo = round(preco * custo_percentual[categoria], 2)
    dias_offset = random.randint(0, (data_fim - data_inicio).days)
    data_venda = data_inicio + timedelta(days=dias_offset)

    vendas.append({
        "id_venda": venda_id,
        "data_venda": data_venda.strftime("%Y-%m-%d"),
        "id_cliente": cliente_id,
        "id_produto": produto_id,
        "categoria": categoria,
        "quantidade": qtd,
        "preco_unitario": preco,
        "custo_unitario": custo
    })
    venda_id += 1

df_vendas = pd.DataFrame(vendas)
df_vendas.to_csv("data/vendas.csv", index=False)
print(f"Vendas: {len(df_vendas)} registros criados")
print("Dados gerados com sucesso!")
