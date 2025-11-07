import docx
import sqlite3
import os

CAMINHO_ARQUIVO_WORD = "data/relatorio_crm.docx" # Baseado em 'image_acc82a.png'
CAMINHO_BANCO = "data/projetos_sonae.db"

def processar_dados_word():
    conexao = None
    try:
        # --- ETAPA 1: LER O ARQUIVO WORD ---
        documento = docx.Document(CAMINHO_ARQUIVO_WORD)
        print(f"Arquivo '{CAMINHO_ARQUIVO_WORD}' lido com sucesso.")

        # --- ETAPA 2: A "PESCARIA" AVANÇADA (DETETIVE 3.1 - CORRIGIDO) ---
        print("Iniciando 'modo detetive 3.1' para extrair seções...")
        
        dados_encontrados = {}
        modo_captura = None 
        texto_capturado = [] 

        # --- MARCADORES CORRIGIDOS (Baseado em image_acc82a.png) ---
        MARCADORES = {
            "Nome do Projeto:": "nome_projeto", # CORRIGIDO
            "Responsável:": "responsavel",
            "Status:": "status",
            "Data:": "data_ultima_atualizacao",
            "1. Resumo Executivo": "resumo_executivo", # Manteve o ':' fora
            "2. Progresso Atual": "progresso_atual",
            "3. Principais Desafios": "principais_desafios",
            "4. Ações Corretivas": "acoes_corretivas",
            "5. Perspectiva": "perspectiva"
        }
        
        for paragrafo in documento.paragraphs:
            texto_linha = paragrafo.text.strip()
            if not texto_linha:
                continue

            novo_modo = None
            
            # Verifica se a linha é um dos nossos marcadores
            for marcador, chave in MARCADORES.items():
                if texto_linha.startswith(marcador):
                    novo_modo = chave
                    
                    # --- Lógica de captura de linha única (para campos simples) ---
                    # (Como "Nome do Projeto:", "Status:", etc.)
                    if chave in ["nome_projeto", "responsavel", "status", "data_ultima_atualizacao"]:
                        dados_encontrados[chave] = texto_linha.split(':', 1)[1].strip()
                        novo_modo = None # Não entra em modo de captura
                    break 

            # Se encontramos um novo marcador de seção (ex: "1. Resumo Executivo")
            if novo_modo:
                if modo_captura and texto_capturado:
                    dados_encontrados[modo_captura] = "\n".join(texto_capturado)
                
                modo_captura = novo_modo 
                texto_capturado = [] 
            
            # Se não é um marcador, mas estamos em modo de captura
            elif modo_captura:
                # Se a linha começar com um traço (lista), formata ela
                if texto_linha.startswith("-"):
                    texto_capturado.append(f"• {texto_linha[1:].strip()}")
                else:
                    texto_capturado.append(texto_linha)

        # Salva a última seção capturada
        if modo_captura and texto_capturado:
            dados_encontrados[modo_captura] = "\n".join(texto_capturado)

        # --- ETAPA 3: VERIFICAR SE ACHAMOS O BÁSICO ---
        if 'nome_projeto' not in dados_encontrados:
            print("ERRO: Não foi possível encontrar o marcador 'Nome do Projeto:' no documento.")
            return 

        print(f"Dados detalhados extraídos para o projeto: {dados_encontrados.get('nome_projeto')}")

        # --- ETAPA 4: LÓGICA UPSERT (Atualizada) ---
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()

        nome = dados_encontrados.get('nome_projeto')
        
        dados_completos = {
            "responsavel": dados_encontrados.get('responsavel'),
            "status": dados_encontrados.get('status'),
            "data_ultima_atualizacao": dados_encontrados.get('data_ultima_atualizacao'),
            "fonte_dados": CAMINHO_ARQUIVO_WORD,
            "resumo_executivo": dados_encontrados.get('resumo_executivo'),
            "progresso_atual": dados_encontrados.get('progresso_atual'),
            "principais_desafios": dados_encontrados.get('principais_desafios'),
            "acoes_corretivas": dados_encontrados.get('acoes_corretivas'),
            "perspectiva": dados_encontrados.get('perspectiva')
        }

        cursor.execute("SELECT id FROM projetos WHERE nome_projeto = ?", (nome,))
        projeto_existente = cursor.fetchone()

        if projeto_existente:
            id_projeto = projeto_existente[0]
            sql_update = """
            UPDATE projetos SET 
                responsavel = ?, status = ?, data_ultima_atualizacao = ?, fonte_dados = ?,
                resumo_executivo = ?, progresso_atual = ?, principais_desafios = ?,
                acoes_corretivas = ?, perspectiva = ?
            WHERE id = ?
            """
            valores = list(dados_completos.values()) + [id_projeto]
            cursor.execute(sql_update, valores)
            print(f"Sucesso! Projeto '{nome}' foi ATUALIZADO no banco com detalhes completos.")
        else:
            # (Esta lógica de INSERT está correta, mas nosso projeto já existe)
            sql_insert = """
            INSERT INTO projetos (
                nome_projeto, responsavel, status, data_ultima_atualizacao, fonte_dados,
                resumo_executivo, progresso_atual, principais_desafios,
                acoes_corretivas, perspectiva
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            valores = [nome] + list(dados_completos.values())
            cursor.execute(sql_insert, valores)
            print(f"Sucesso! Projeto '{nome}' foi INSERIDO no banco com detalhes completos.")

        conexao.commit()

    except Exception as e:
        print(f"ERRO inesperado ao processar Word: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    processar_dados_word()