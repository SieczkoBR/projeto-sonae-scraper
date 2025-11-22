import pandas as pd
import sqlite3
import os
# Importamos a função de segurança
from seguranca import encriptar_dado

CAMINHO_ARQUIVO_EXCEL = "data/relatorios_sonae.xlsx"
CAMINHO_BANCO = "data/projetos_sonae.db"

def processar_dados_excel():
    conexao = None
    try:
        # --- ETAPA 1: LER O EXCEL ---
        # header=1 porque a primeira linha do seu Excel é vazia/título
        dataframe = pd.read_excel(CAMINHO_ARQUIVO_EXCEL, header=1)
        print(f"Arquivo '{CAMINHO_ARQUIVO_EXCEL}' lido com sucesso.")

        # --- ETAPA 2: CONECTAR AO BANCO ---
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        print(f"Conexão com o banco '{CAMINHO_BANCO}' estabelecida.")

        print("Iniciando lógica UPSERT com Criptografia...")
        linhas_atualizadas = 0
        linhas_inseridas = 0

        for index, linha in dataframe.iterrows():
            nome = linha['Nome do Projeto']
            status = linha['Status']
            # AQUI APLICAMOS A SEGURANÇA:
            responsavel_bruto = linha['Responsavel']
            responsavel_seguro = encriptar_dado(responsavel_bruto)
            
            data_atualizacao = str(linha['Ultima Atualizacao'])
            fonte = CAMINHO_ARQUIVO_EXCEL

            # --- ETAPA 3: VERIFICAR SE O PROJETO JÁ EXISTE ---
            cursor.execute("SELECT id FROM projetos WHERE nome_projeto = ?", (nome,))
            projeto_existente = cursor.fetchone()

            if projeto_existente:
                # --- UPDATE (Atualiza com o nome criptografado) ---
                id_projeto = projeto_existente[0]
                sql_update = """
                UPDATE projetos 
                SET responsavel = ?, status = ?, data_ultima_atualizacao = ?, fonte_dados = ?
                WHERE id = ?
                """
                cursor.execute(sql_update, (responsavel_seguro, status, data_atualizacao, fonte, id_projeto))
                linhas_atualizadas += 1
            else:
                # --- INSERT (Insere com o nome criptografado) ---
                sql_insert = """
                INSERT INTO projetos (nome_projeto, responsavel, status, data_ultima_atualizacao, fonte_dados)
                VALUES (?, ?, ?, ?, ?);
                """
                cursor.execute(sql_insert, (nome, responsavel_seguro, status, data_atualizacao, fonte))
                linhas_inseridas += 1

        # --- ETAPA 5: SALVAR ---
        conexao.commit()
        print(f"Sucesso! {linhas_inseridas} linhas novas inseridas.")
        print(f"Sucesso! {linhas_atualizadas} linhas existentes foram atualizadas.")

    except Exception as e:
        print(f"ERRO inesperado ao processar Excel: {e}")
        if conexao:
            conexao.rollback()
            
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    processar_dados_excel()