import sqlite3
import os
from transformers import pipeline

# --- Configuração ---
CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")

# --- ETAPA 1: Carregar o Modelo de IA (Download Único) ---
# Na primeira vez que rodar, ele vai baixar o modelo (pode demorar).
# Usamos o "t5-small", um modelo leve e eficiente para resumos.
print("Carregando modelo de IA (t5-small)... Isso pode demorar na primeira vez.")
try:
    # "summarization" é a tarefa que queremos
    summarizer = pipeline("summarization", model="t5-small")
    print("Modelo de IA carregado com sucesso.")
except Exception as e:
    print(f"ERRO ao carregar o modelo de IA. Verifique sua conexão ou a instalação do transformers.")
    print(f"Detalhe do erro: {e}")
    exit() # Encerra o script se não puder carregar a IA

# --- Função de Conexão (Helper) ---
def get_db_connection():
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.row_factory = sqlite3.Row # Para acessar por nome
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

# --- ETAPA 2: Processar os Dados ---
def gerar_insights():
    conexao = get_db_connection()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()
        
        # Selecionamos projetos que têm um resumo, mas AINDA NÃO têm um insight de IA
        cursor.execute("""
            SELECT id, nome_projeto, resumo_executivo, principais_desafios 
            FROM projetos 
            WHERE resumo_ia IS NULL 
            AND (resumo_executivo IS NOT NULL OR principais_desafios IS NOT NULL)
        """)
        
        projetos_para_processar = cursor.fetchall()
        
        if not projetos_para_processar:
            print("Nenhum projeto novo para processar. O banco já está atualizado.")
            return

        print(f"Encontrados {len(projetos_para_processar)} projetos para gerar insights...")

        for projeto in projetos_para_processar:
            # Criamos o texto que a IA vai ler
            texto_para_resumir = ""
            if projeto['resumo_executivo']:
                texto_para_resumir += f"Resumo: {projeto['resumo_executivo']}\n"
            if projeto['principais_desafios']:
                texto_para_resumir += f"Desafios: {projeto['principais_desafios']}\n"
            
            if not texto_para_resumir:
                continue

            # --- ETAPA 3: Usar a IA para Gerar o Resumo ---
            # O T5 espera um prefixo "summarize: "
            # max_length=50: Insight curto (aprox 50 palavras)
            # min_length=10: Insight mínimo
            insight_bruto = summarizer(
                "summarize: " + texto_para_resumir, 
                max_length=50, 
                min_length=10, 
                do_sample=False
            )
            
            insight_texto = insight_bruto[0]['summary_text']
            
            print(f"Insight gerado para '{projeto['nome_projeto']}': {insight_texto}")

            # --- ETAPA 4: Salvar o Insight no Banco ---
            cursor.execute(
                "UPDATE projetos SET resumo_ia = ? WHERE id = ?",
                (insight_texto, projeto['id'])
            )

        conexao.commit()
        print(f"Sucesso! {len(projetos_para_processar)} projetos atualizados com insights da IA.")

    except Exception as e:
        print(f"ERRO durante o processamento dos insights: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco fechada.")

# --- Executa a função principal ---
if __name__ == "__main__":
    gerar_insights()