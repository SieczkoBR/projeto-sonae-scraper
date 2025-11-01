import docx
import sqlite3
import os

CAMINHO_ARQUIVO_WORD = "data/relatorio_crm.docx"
CAMINHO_BANCO = "data/projetos_sonae.db"

def processar_dados_word():
    conexao = None
    try:
        # --- ETAPA 1: LER O ARQUIVO WORD (Sem mudanças) ---
        documento = docx.Document(CAMINHO_ARQUIVO_WORD)
        print(f"Arquivo '{CAMINHO_ARQUIVO_WORD}' lido com sucesso.")

        # --- ETAPA 2: A "PESCARIA" INTELIGENTE (Sem mudanças) ---
        dados_encontrados = {}
        print("Iniciando 'modo detetive' para extrair dados do texto...")
        
        for paragrafo in documento.paragraphs:
            texto_linha = paragrafo.text.strip() 

            if texto_linha.startswith("Nome do Projeto:"):
                dados_encontrados['nome'] = texto_linha.split(':', 1)[1].strip()
            elif texto_linha.startswith("Responsável:"):
                dados_encontrados['responsavel'] = texto_linha.split(':', 1)[1].strip()
            elif texto_linha.startswith("Status Atual:"):
                dados_encontrados['status'] = texto_linha.split(':', 1)[1].strip()
            elif texto_linha.startswith("Data do Relatório:"):
                dados_encontrados['data'] = texto_linha.split(':', 1)[1].strip()

        # --- ETAPA 3: VERIFICAR SE ACHAMOS O BÁSICO (Sem mudanças) ---
        if 'nome' not in dados_encontrados:
            print("ERRO: Não foi possível encontrar a linha 'Nome do Projeto:' no documento.")
            return 

        print(f"Dados extraídos com sucesso para o projeto: {dados_encontrados.get('nome')}")

        # --- ETAPA 4: LÓGICA UPSERT (A NOVA INTELIGÊNCIA) ---
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()

        # Preparar os dados para o banco
        nome = dados_encontrados.get('nome')
        responsavel = dados_encontrados.get('responsavel')
        status = dados_encontrados.get('status')
        data_atualizacao = dados_encontrados.get('data')
        fonte = CAMINHO_ARQUIVO_WORD

        # Verificar se o projeto já existe
        cursor.execute("SELECT id FROM projetos WHERE nome_projeto = ?", (nome,))
        projeto_existente = cursor.fetchone()

        if projeto_existente:
            # O PROJETO EXISTE! VAMOS ATUALIZAR (UPDATE)
            id_projeto = projeto_existente[0]
            sql_update = """
            UPDATE projetos 
            SET responsavel = ?, status = ?, data_ultima_atualizacao = ?, fonte_dados = ?
            WHERE id = ?
            """
            cursor.execute(sql_update, (responsavel, status, data_atualizacao, fonte, id_projeto))
            print(f"Sucesso! Projeto '{nome}' foi ATUALIZADO no banco.")
        
        else:
            # PROJETO NOVO! VAMOS INSERIR (INSERT)
            sql_insert = """
            INSERT INTO projetos (nome_projeto, responsavel, status, data_ultima_atualizacao, fonte_dados)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor.execute(sql_insert, (nome, responsavel, status, data_atualizacao, fonte))
            print(f"Sucesso! Projeto '{nome}' foi INSERIDO no banco.")

        # --- ETAPA 5: SALVAR TUDO NO BANCO ---
        conexao.commit()

    except Exception as e:
        print(f"ERRO inesperado ao processar Word: {e}")
        if conexao:
            conexao.rollback()
            
    finally:
        # --- ETAPA 6: FECHAR A CONEXÃO ---
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    processar_dados_word()