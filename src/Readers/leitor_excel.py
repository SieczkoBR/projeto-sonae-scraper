import pandas as pd
import sqlite3
import os

CAMINHO_ARQUIVO_EXCEL = "data/relatorios_sonae.xlsx"
CAMINHO_BANCO = "data/projetos_sonae.db"

def processar_dados_excel():
    conexao = None
    try:
        # --- ETAPA 1: LER O EXCEL (Sem mudanças) ---
        dataframe = pd.read_excel(CAMINHO_ARQUIVO_EXCEL, header=1)
        print(f"Arquivo '{CAMINHO_ARQUIVO_EXCEL}' lido com sucesso.")

        # --- ETAPA 2: CONECTAR AO BANCO (Sem mudanças) ---
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        print(f"Conexão com o banco '{CAMINHO_BANCO}' estabelecida.")

        print("Iniciando lógica UPSERT (Update/Insert)...")
        linhas_atualizadas = 0
        linhas_inseridas = 0

        for index, linha in dataframe.iterrows():
            nome = linha['Nome do Projeto']
            status = linha['Status']
            responsavel = linha['Responsavel']
            data_atualizacao = str(linha['Ultima Atualizacao'])
            fonte = CAMINHO_ARQUIVO_EXCEL

            # --- ETAPA 3: VERIFICAR SE O PROJETO JÁ EXISTE ---
            # Aqui está a nova inteligência:
            cursor.execute("SELECT id FROM projetos WHERE nome_projeto = ?", (nome,))
            projeto_existente = cursor.fetchone() # Pega a primeira linha que encontrar

            if projeto_existente:
                # --- ETAPA 4 (A): O PROJETO EXISTE! VAMOS ATUALIZAR (UPDATE) ---
                id_projeto = projeto_existente[0]
                sql_update = """
                UPDATE projetos 
                SET responsavel = ?, status = ?, data_ultima_atualizacao = ?, fonte_dados = ?
                WHERE id = ?
                """
                cursor.execute(sql_update, (responsavel, status, data_atualizacao, fonte, id_projeto))
                linhas_atualizadas += 1
            
            else:
                # --- ETAPA 4 (B): PROJETO NOVO! VAMOS INSERIR (INSERT) ---
                sql_insert = """
                INSERT INTO projetos (nome_projeto, responsavel, status, data_ultima_atualizacao, fonte_dados)
                VALUES (?, ?, ?, ?, ?);
                """
                cursor.execute(sql_insert, (nome, responsavel, status, data_atualizacao, fonte))
                linhas_inseridas += 1

        # --- ETAPA 5: SALVAR TUDO NO BANCO ---
        conexao.commit()
        print(f"Sucesso! {linhas_inseridas} linhas novas inseridas.")
        print(f"Sucesso! {linhas_atualizadas} linhas existentes foram atualizadas.")

    except Exception as e:
        print(f"ERRO inesperado ao processar Excel: {e}")
        if conexao:
            conexao.rollback() # Desfaz qualquer mudança se der erro
            
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    processar_dados_excel()