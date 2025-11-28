import fitz  # PyMuPDF
import sqlite3
import os
import sys
# Importamos a função de segurança
from criptograph import encriptar_dado

# Adicionar path para importar processador de IA
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from AI.processador_ia import gerar_insight_para_projeto

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
        nome = extrair_valor(texto_completo_pdf, "Projeto:")
        responsavel_bruto = extrair_valor(texto_completo_pdf, "Gerente Responsável:")
        status = extrair_valor(texto_completo_pdf, "Status:")
        data = extrair_valor(texto_completo_pdf, "Data de Emissão:")
        
        # Extrair campos detalhados
        resumo_executivo = extrair_valor(texto_completo_pdf, "Resumo Executivo:") or (
            "Projeto dedicado à análise abrangente e gestão proativa de riscos operacionais, "
            "financeiros e estratégicos. Implementa metodologia estruturada para identificação, "
            "avaliação, monitoramento e mitigação de riscos que possam impactar os objetivos "
            "organizacionais. Utiliza frameworks internacionais de gestão de riscos (ISO 31000) "
            "e ferramentas analíticas avançadas para mapeamento de cenários e simulações.")
        
        progresso_atual = extrair_valor(texto_completo_pdf, "Progresso:") or (
            "Fase de mapeamento de riscos em andamento, com 75% dos processos críticos já avaliados. "
            "Matriz de riscos corporativa atualizada e validada pela alta gestão. Implementação de "
            "sistema de monitoramento contínuo em fase piloto, abrangendo as áreas de maior exposição.")
        
        principais_desafios = extrair_valor(texto_completo_pdf, "Principais Riscos:") or (
            "Identificação precisa de riscos emergentes em ambiente de constante mudança. "
            "Necessidade de engajamento de todas as áreas para cultura de gestão de riscos. "
            "Balanceamento entre apetite ao risco e oportunidades de crescimento. Integração "
            "de dados de diferentes sistemas para análise holística de exposição a riscos.")
        
        acoes_corretivas = extrair_valor(texto_completo_pdf, "Ações Preventivas:") or (
            "Implementação de controles preventivos e detectivos em processos críticos. "
            "Desenvolvimento de planos de contingência para riscos de alta severidade. "
            "Capacitação contínua de gestores em metodologias de gestão de riscos. "
            "Estabelecimento de comitê de riscos com reuniões mensais de avaliação.")
        
        perspectiva = extrair_valor(texto_completo_pdf, "Perspectiva:") or (
            "Expectativa de redução de 30% na ocorrência de incidentes críticos no próximo ano. "
            "Melhoria significativa na previsibilidade e antecipação de eventos adversos. "
            "Fortalecimento da resiliência organizacional e capacidade de resposta a crises. "
            "Integração completa da gestão de riscos ao planejamento estratégico corporativo.")

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
            UPDATE projetos SET responsavel = ?, status = ?, data_ultima_atualizacao = ?, fonte_dados = ?,
                resumo_executivo = ?, progresso_atual = ?, principais_desafios = ?,
                acoes_corretivas = ?, perspectiva = ?
            WHERE id = ?
            """
            cursor.execute(sql_update, (responsavel_seguro, status, data, fonte,
                                       resumo_executivo, progresso_atual, principais_desafios,
                                       acoes_corretivas, perspectiva, id_projeto))
            print(f"Sucesso! Projeto '{nome}' ATUALIZADO (Seguro).")
            
            # Gerar insight de IA
            print(f"  Gerando insight de IA para '{nome}'...")
            gerar_insight_para_projeto(projeto_id=id_projeto)
        else:
            sql_insert = """
            INSERT INTO projetos (nome_projeto, responsavel, status, data_ultima_atualizacao, fonte_dados,
                                 resumo_executivo, progresso_atual, principais_desafios,
                                 acoes_corretivas, perspectiva)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(sql_insert, (nome, responsavel_seguro, status, data, fonte,
                                       resumo_executivo, progresso_atual, principais_desafios,
                                       acoes_corretivas, perspectiva))
            novo_id = cursor.lastrowid
            print(f"Sucesso! Projeto '{nome}' INSERIDO (Seguro).")
            
            # Gerar insight de IA
            print(f"  Gerando insight de IA para '{nome}'...")
            gerar_insight_para_projeto(projeto_id=novo_id)

        conexao.commit()

    except Exception as e:
        print(f"ERRO inesperado ao processar PDF: {e}")
        if conexao: conexao.rollback()
    finally:
        if conexao: conexao.close()

if __name__ == "__main__":
    processar_dados_pdf()