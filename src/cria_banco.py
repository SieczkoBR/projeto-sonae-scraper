import docx
import sqlite3
import os

CAMINHO_ARQUIVO_WORD = "data/relatorio_crm.docx" # Verifique se este arquivo tem a nova estrutura!
CAMINHO_BANCO = "data/projetos_sonae.db"

def processar_dados_word():
    conexao = None
    try:
        # --- ETAPA 1: LER O ARQUIVO WORD ---
        documento = docx.Document(CAMINHO_ARQUIVO_WORD)
        print(f"Arquivo '{CAMINHO_ARQUIVO_WORD}' lido com sucesso.")

        # --- ETAPA 2: A "PESCARIA" AVANÇADA (DETETIVE 3.0) ---
        print("Iniciando 'modo detetive 3.0' para extrair seções...")
        
        dados_encontrados = {}
        modo_captura = None # Qual seção estamos capturando agora?
        texto_capturado = [] # Lista para guardar as linhas da seção

        # Marcadores que definem o início de uma nova seção
        # (Baseado no Figma image_a8ebe2.png)
        MARCADORES = {
            "Relatório de Andamento": "nome_projeto",
            "Responsável:": "responsavel",
            "Status:": "status",
            "Data:": "data_ultima_atualizacao",
            "1. Resumo Executivo": "resumo_executivo",
            "2. Progresso Atual": "progresso_atual",
            "3. Principais Desafios": "principais_desafios",
            "4. Ações Corretivas": "acoes_corretivas",
            "5. Perspectiva": "perspectiva"
        }
        
        for paragrafo in documento.paragraphs:
            texto_linha = paragrafo.text.strip()
            if not texto_linha: # Ignora linhas em branco
                continue

            novo_modo = None
            # Verifica se a linha é um dos nossos marcadores principais
            for marcador, chave in MARCADORES.items():
                if texto_linha.startswith(marcador):
                    novo_modo = chave
                    
                    # --- Lógica de captura de linha única (para campos simples) ---
                    if chave in ["responsavel", "status", "data_ultima_atualizacao"]:
                        dados_encontrados[chave] = texto_linha.split(':', 1)[1].strip()
                        novo_modo = None # Não entra em modo de captura para campos simples
                    elif chave == "nome_projeto":
                        # Ex: "Relatório de Andamento — Projeto "Monitor de Indicadores""
                        dados_encontrados[chave] = texto_linha.split('— Projeto "')[1].replace('"', '').strip()
                        novo_modo = None
                    break # Achamos um marcador, paramos de procurar

            # Se encontramos um novo marcador de seção (ex: "1. Resumo Executivo")
            if novo_modo:
                # Se estávamos capturando algo antes (ex: o Resumo), salvamos
                if modo_captura and texto_capturado:
                    dados_encontrados[modo_captura] = "\n".join(texto_capturado) # Salva o texto como um bloco
                
                modo_captura = novo_modo # Inicia a nova captura
                texto_capturado = [] # Limpa a lista
            
            # Se não é um marcador, mas estamos em modo de captura
            elif modo_captura:
                texto_capturado.append(texto_linha) # Adiciona a linha ao bloco

        # Salva a última seção capturada (ex: a "5. Perspectiva")
        if modo_captura and texto_capturado:
            dados_encontrados[modo_captura] = "\n".join(texto_capturado)

        # --- ETAPA 3: VERIFICAR SE ACHAMOS O BÁSICO ---
        if 'nome_projeto' not in dados_encontrados:
            print("ERRO: Não foi possível encontrar o marcador 'Relatório de Andamento — Projeto ...'")
            return 

        print(f"Dados detalhados extraídos para o projeto: {dados_encontrados.get('nome_projeto')}")

        # --- ETAPA 4: LÓGICA UPSERT (AGORA COM AS NOVAS COLUNAS) ---
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()

        nome = dados_encontrados.get('nome_projeto')
        
        # Prepara todos os dados (usando .get() para segurança)
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
            # UPDATE (Atualiza todas as novas colunas)
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
            # INSERT (Insere todas as novas colunas)
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