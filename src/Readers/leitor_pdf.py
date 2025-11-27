# Trocamos PyPDF2 por fitz (PyMuPDF)
import fitz  # PyMuPDF
import sqlite3
import os

CAMINHO_ARQUIVO_PDF = "data/relatorio_riscos.pdf"
CAMINHO_BANCO = "data/projetos_sonae.db"

# --- Função Ajudante "Detetive 2.0" (Sem mudanças) ---
# Esta função deve funcionar agora que o texto virá limpo
def extrair_valor(texto_completo, marcador):
    try:
        texto_lower = texto_completo.lower()
        marcador_lower = marcador.lower()
        inicio = texto_lower.find(marcador_lower)
        if inicio == -1:
            return None
        texto_a_partir_do_marcador = texto_completo[inicio + len(marcador):]
        # O .split('\n')[0] agora deve pegar a linha correta!
        valor = texto_a_partir_do_marcador.split('\n')[0]
        return valor.strip().replace(":", "") # Adiciona uma limpeza extra
    except Exception:
        return None

# --- Função Principal Atualizada ---
def processar_dados_pdf():
    conexao = None
    try:
        # --- ETAPA 1: LER O PDF (AGORA COM PyMuPDF/fitz) ---
        texto_completo_pdf = ""
        # fitz.open é o novo comando para abrir o PDF
        with fitz.open(CAMINHO_ARQUIVO_PDF) as doc:
            for pagina in doc:
                # page.get_text() é o novo comando para extrair o texto
                texto_completo_pdf += pagina.get_text() + "\n"
                
        print(f"Arquivo '{CAMINHO_ARQUIVO_PDF}' lido com sucesso (usando PyMuPDF).")

        # --- ETAPA 2: "PESCARIA" (Sem mudanças) ---
        print("Iniciando 'modo detetive' (versão 3.0)...")
        
        # Agora, estes marcadores devem ser encontrados no texto limpo
        nome = extrair_valor(texto_completo_pdf, "Projeto:")
        responsavel = extrair_valor(texto_completo_pdf, "Gerente Responsável:")
        status = extrair_valor(texto_completo_pdf, "Status:")
        data = extrair_valor(texto_completo_pdf, "Data de Emissão:")

        # --- ETAPA 3: VERIFICAR SE ACHAMOS O BÁSICO (Sem mudanças) ---
        if not nome:
            print("ERRO: Não foi possível extrair o 'Nome do Projeto' do PDF.")
            print("Verifique se o marcador 'Projeto:' está correto.")
            return 

        print(f"Dados extraídos com sucesso para o projeto: {nome}")

        # --- ETAPA 4: LÓGICA UPSERT (Sem mudanças) ---
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        fonte = CAMINHO_ARQUIVO_PDF

        cursor.execute("SELECT id FROM projetos WHERE nome_projeto = ?", (nome,))
        projeto_existente = cursor.fetchone()

        if projeto_existente:
            id_projeto = projeto_existente[0]
            sql_update = """
            UPDATE projetos SET responsavel = ?, status = ?, data_ultima_atualizacao = ?, fonte_dados = ?
            WHERE id = ?
            """
            cursor.execute(sql_update, (responsavel, status, data, fonte, id_projeto))
            print(f"Sucesso! Projeto '{nome}' foi ATUALIZADO no banco.")
        else:
            sql_insert = """
            INSERT INTO projetos (nome_projeto, responsavel, status, data_ultima_atualizacao, fonte_dados)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor.execute(sql_insert, (nome, responsavel, status, data, fonte))
            print(f"Sucesso! Projeto '{nome}' foi INSERIDO no banco.")

        # --- ETAPA 5: SALVAR TUDO NO BANCO ---
        conexao.commit()

    except Exception as e:
        print(f"ERRO inesperado ao processar PDF: {e}")
        if conexao:
            conexao.rollback()
            
    finally:
        # --- ETAPA 6: FECHAR A CONEXÃO ---
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    processar_dados_pdf()