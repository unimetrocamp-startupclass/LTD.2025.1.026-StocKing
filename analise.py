import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURAÇÃO ---
sns.set_theme(style="whitegrid")

# Define o nome da pasta de saída para os gráficos
output_folder = 'graficos'

# Caminho para o banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'estoque.db')
engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

# --- CRIA A PASTA DE GRÁFICOS (SE NÃO EXISTIR) ---
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Pasta '{output_folder}' criada com sucesso!")

print("\n--- Lendo dados do banco... ---")
try:
    df_products = pd.read_sql_table('products', engine)
    df_users = pd.read_sql_table('users', engine)
    print("Dados lidos com sucesso!")
except ValueError:
    print("Tabelas não encontradas. O banco de dados parece estar vazio.")
    df_products = pd.DataFrame()
    df_users = pd.DataFrame()

# --- ANÁLISE E VISUALIZAÇÃO ---
if not df_products.empty:
    df_completo = pd.merge(df_products, df_users, left_on='user_id', right_on='id', suffixes=('', '_usuario'))
    tabela_final = df_completo[['id', 'codigo', 'nome', 'quantidade', 'tipo_servico', 'data_recebimento', 'data_envio_previsto', 'nome_usuario']]
    tabela_final = tabela_final.rename(columns={'nome_usuario': 'cadastrado_por'})

    print("\n--- Tabela de Produtos Cadastrados ---")
    print(tabela_final.to_string())

    # --- Salva a tabela em um arquivo CSV dentro da pasta de gráficos ---
    caminho_csv = os.path.join(output_folder, 'tabela_produtos.csv')
    tabela_final.to_csv(caminho_csv, index=False, sep=';')
    print(f"\nTabela de produtos também salva em '{caminho_csv}'")


    # 1. Gráfico: Contagem de produtos por Tipo de Serviço
    print("\n--- Gerando gráfico por Tipo de Serviço... ---")
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(data=df_products, y='tipo_servico', order=df_products['tipo_servico'].value_counts().index)
    ax.set_title('Distribuição de Produtos por Tipo de Serviço', fontsize=16)
    ax.set_xlabel('Contagem de Produtos', fontsize=12)
    ax.set_ylabel('Tipo de Serviço', fontsize=12)
    plt.tight_layout()
    # --- ALTERAÇÃO: Salva o gráfico dentro da pasta 'graficos' ---
    caminho_grafico = os.path.join(output_folder, 'grafico_tipo_servico.png')
    plt.savefig(caminho_grafico)
    print(f"Gráfico salvo em '{caminho_grafico}'")

    # 2. Gráfico: Cadastros de produto por usuário
    print("\n--- Gerando gráfico por Usuário... ---")
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(data=tabela_final, y='cadastrado_por', order=tabela_final['cadastrado_por'].value_counts().index, palette='viridis')
    ax.set_title('Produtos Cadastrados por Usuário', fontsize=16)
    ax.set_xlabel('Contagem de Produtos', fontsize=12)
    ax.set_ylabel('Usuário', fontsize=12)
    plt.tight_layout()
    # --- ALTERAÇÃO: Salva o gráfico dentro da pasta 'graficos' ---
    caminho_grafico = os.path.join(output_folder, 'grafico_por_usuario.png')
    plt.savefig(caminho_grafico)
    print(f"Gráfico salvo em '{caminho_grafico}'")

    # 3. Gráfico: Evolução de cadastros ao longo do tempo
    print("\n--- Gerando gráfico de evolução no tempo... ---")
    df_products['data_recebimento'] = pd.to_datetime(df_products['data_recebimento'])
    produtos_por_mes = df_products.set_index('data_recebimento').resample('ME').size()
    plt.figure(figsize=(12, 6))
    ax = produtos_por_mes.plot(kind='line', marker='o', linestyle='-')
    ax.set_title('Evolução de Cadastros de Produtos por Mês', fontsize=16)
    ax.set_xlabel('Mês de Recebimento', fontsize=12)
    ax.set_ylabel('Número de Produtos Cadastrados', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    # --- ALTERAÇÃO: Salva o gráfico dentro da pasta 'graficos' ---
    caminho_grafico = os.path.join(output_folder, 'grafico_evolucao_tempo.png')
    plt.savefig(caminho_grafico)
    print(f"Gráfico salvo em '{caminho_grafico}'")

else:
    print("\nO banco de dados não contém produtos. Nenhum gráfico ou tabela será gerado.")