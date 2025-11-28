import fitz  # PyMuPDF
import sqlite3
import os
# Importamos a função de segurança
from criptograph import encriptar_dado

CAMINHO_ARQUIVO_PDF = "data/relatorio_riscos.pdf"
CAMINHO_BANCO = "data/projetos_sonae.db"

def extrair_valor(texto_completo, marcador):
    try:
        texto_lower = texto_completo.lower()
        marcador_lower = marcador.lower()
        inicio = texto_lower.find(marcador_lower)
        if inicio == -1:
            return None
        texto_a_partir_do_marcador = texto_completo[inicio + len(marcador):]
        valor = texto_a_partir_do_marcador.split('\n')[0]
        return valor.strip().replace(":", "")
    except Exception:
        return None

def processar_dados_pdf():
    conexao = None
    try:
        # --- ETAPA 1: LER O PDF ---
        texto_completo_pdf = ""
        with fitz.open(CAMINHO_ARQUIVO_PDF) as doc:
            for pagina in doc:
                texto_completo_pdf += pagina.get_text() + "\n"
        print(f"Arquivo '{CAMINHO_ARQUIVO_PDF}' lido com sucesso.")

        # --- ETAPA 2: PESCARIA ---
        print("Iniciando 'modo detetive'...")
        nome = extrair_valor(texto_completo_pdf, "Projeto:") # Ajuste conforme seu PDF
        responsavel_bruto = extrair_valor(texto_completo_pdf, "Gerente Responsável:")
        status = extrair_valor(texto_completo_pdf, "Status:")
        data = extrair_valor(texto_completo_pdf, "Data de Emissão:")

        if not nome:
            print("ERRO: Não foi possível extrair o 'Nome do Projeto' do PDF.")
            return 

        print(f"Dados extraídos para: {nome}")

        # --- ETAPA 3: UPSERT COM SEGURANÇA ---
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        fonte = CAMINHO_ARQUIVO_PDF
        
        # AQUI APLICAMOS A SEGURANÇA:
        responsavel_seguro = encriptar_dado(responsavel_bruto)

        cursor.execute("SELECT id FROM projetos WHERE nome_projeto = ?", (nome,))
        projeto_existente = cursor.fetchone()

        if projeto_existente:
            id_projeto = projeto_existente[0]
            sql_update = """
            UPDATE projetos SET responsavel = ?, status = ?, data_ultima_atualizacao = ?, fonte_dados = ?
            WHERE id = ?
            """
            cursor.execute(sql_update, (responsavel_seguro, status, data, fonte, id_projeto))
            print(f"Sucesso! Projeto '{nome}' ATUALIZADO (Seguro).")
        else:
            sql_insert = """
            INSERT INTO projetos (nome_projeto, responsavel, status, data_ultima_atualizacao, fonte_dados)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor.execute(sql_insert, (nome, responsavel_seguro, status, data, fonte))
            print(f"Sucesso! Projeto '{nome}' INSERIDO (Seguro).")

        conexao.commit()

    except Exception as e:
        print(f"ERRO inesperado ao processar PDF: {e}")
        if conexao: conexao.rollback()
    finally:
        if conexao: conexao.close()

if __name__ == "__main__":
    processar_dados_pdf()