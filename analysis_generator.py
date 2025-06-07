import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from matplotlib.ticker import MaxNLocator # <-- 1. IMPORTAMOS A FERRAMENTA NECESSÁRIA

def generate_reports():
    """
    Função principal que lê os dados, gera e salva os relatórios (gráficos e CSV).
    Retorna o caminho completo do arquivo CSV para download.
    """
    sns.set_theme(style="whitegrid")
    output_folder = 'relatorios'
    basedir = os.path.abspath(os.path.dirname(__file__))
    reports_path = os.path.join(basedir, output_folder)
    db_path = os.path.join(basedir, 'instance', 'estoque.db')
    engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

    if not os.path.exists(reports_path):
        os.makedirs(reports_path)
        print(f"Pasta '{output_folder}' criada com sucesso!")

    print("\n--- Lendo dados do banco... ---")
    try:
        df_products = pd.read_sql_table('products', engine)
        df_users = pd.read_sql_table('users', engine)
        print("Dados lidos com sucesso!")
    except ValueError:
        print("Tabelas não encontradas. O banco de dados parece estar vazio.")
        return None

    if df_products.empty:
        print("\nO banco de dados não contém produtos. Nenhum relatório será gerado.")
        return None

    df_completo = pd.merge(df_products, df_users, left_on='user_id', right_on='id', suffixes=('', '_usuario'))
    tabela_final = df_completo[['id', 'codigo', 'nome', 'quantidade', 'tipo_servico', 'data_recebimento', 'data_envio_previsto', 'nome_usuario']]
    tabela_final = tabela_final.rename(columns={'nome_usuario': 'cadastrado_por'})

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'relatorio_produtos_{timestamp}.csv'
    csv_filepath = os.path.join(reports_path, csv_filename)
    tabela_final.to_csv(csv_filepath, index=False, sep=';', encoding='utf-8-sig')
    print(f"\nTabela de produtos também salva em '{csv_filepath}'")

    # --- GRÁFICO 1: Contagem de produtos por Tipo de Serviço ---
    print("\n--- Gerando gráfico por Tipo de Serviço... ---")
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(data=df_products, y='tipo_servico', order=df_products['tipo_servico'].value_counts().index)
    ax.set_title('Distribuição de Produtos por Tipo de Serviço', fontsize=16)
    ax.set_xlabel('Contagem de Produtos', fontsize=12)
    ax.set_ylabel('Tipo de Serviço', fontsize=12)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True)) # <-- 2. ADICIONAMOS ESTA LINHA PARA FORÇAR NÚMEROS INTEIROS NO EIXO X
    plt.tight_layout()
    caminho_grafico = os.path.join(reports_path, 'grafico_tipo_servico.png')
    plt.savefig(caminho_grafico)
    print(f"Gráfico salvo em '{caminho_grafico}'")
    plt.close()

    # --- GRÁFICO 2: Cadastros de produto por usuário ---
    print("\n--- Gerando gráfico por Usuário... ---")
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(data=tabela_final, y='cadastrado_por', order=tabela_final['cadastrado_por'].value_counts().index, palette='viridis')
    ax.set_title('Produtos Cadastrados por Usuário', fontsize=16)
    ax.set_xlabel('Contagem de Produtos', fontsize=12)
    ax.set_ylabel('Usuário', fontsize=12)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True)) # <-- 3. ADICIONAMOS ESTA LINHA AQUI TAMBÉM
    plt.tight_layout()
    caminho_grafico = os.path.join(reports_path, 'grafico_por_usuario.png')
    plt.savefig(caminho_grafico)
    print(f"Gráfico salvo em '{caminho_grafico}'")
    plt.close()

    # --- GRÁFICO 3: Evolução de cadastros ao longo do tempo ---
    print("\n--- Gerando gráfico de evolução no tempo... ---")
    df_products['data_recebimento'] = pd.to_datetime(df_products['data_recebimento'])
    produtos_por_mes = df_products.set_index('data_recebimento').resample('ME').size()
    plt.figure(figsize=(12, 6))
    ax = produtos_por_mes.plot(kind='line', marker='o', linestyle='-')
    ax.set_title('Evolução de Cadastros de Produtos por Mês', fontsize=16)
    ax.set_xlabel('Mês de Recebimento', fontsize=12)
    ax.set_ylabel('Número de Produtos Cadastrados', fontsize=12)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True)) # <-- 4. E AQUI NO EIXO Y, PARA A CONTAGEM
    plt.grid(True)
    plt.tight_layout()
    caminho_grafico = os.path.join(reports_path, 'grafico_evolucao_tempo.png')
    plt.savefig(caminho_grafico)
    print(f"Gráfico salvo em '{caminho_grafico}'")
    plt.close()

    return csv_filepath