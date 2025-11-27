import sqlite3
import os
from transformers import pipeline
from datetime import datetime
import logging

# --- Criar pasta de logs se nao existir (ANTES de usar) ---
os.makedirs("logs", exist_ok=True)

# --- Configuracao de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/processador_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuracao ---
CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
MODELO = "t5-base"  # Considere mudar para "t5-small" se NAO tiver VRAM suficiente
MAX_LENGTH = 250     
MIN_LENGTH = 50      
BATCH_SIZE = 5

# --- ETAPA 1: Carregar o Modelo de IA ---
def carregar_modelo():
    """Carrega o modelo de IA com tratamento de erro"""
    logger.info(f"Carregando modelo {MODELO}... Isso pode demorar na primeira vez.")
    try:
        summarizer = pipeline("summarization", model=MODELO)
        logger.info("[OK] Modelo de IA carregado com sucesso.")
        return summarizer
    except Exception as e:
        logger.error(f"[ERRO] ao carregar o modelo: {e}")
        logger.error("Verifique sua conexao ou a instalacao do transformers.")
        return None

# --- Funcao de Conexao (Helper) ---
def get_db_connection():
    """Cria conexao com o banco de dados"""
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.row_factory = sqlite3.Row
        return conexao
    except Exception as e:
        logger.error(f"[ERRO] ao conectar ao banco: {e}")
        return None

# --- Funcao para Preparar Texto ---
def preparar_texto(projeto):
    """Prepara e limpa o texto para processamento"""
    texto = ""
    
    if projeto['resumo_executivo']:
        texto += f"{projeto['resumo_executivo']} "
    
    if projeto['principais_desafios']:
        texto += f"{projeto['principais_desafios']} "
    
    # Remove espacos extras e caracteres especiais
    texto = " ".join(texto.split())
    
    # Verifica tamanho minimo
    if len(texto.split()) < 20:
        logger.warning(f"[AVISO] Texto muito curto para '{projeto['nome_projeto']}' - pulando")
        return None
    
    return texto

# --- Funcao para Gerar Insight com Tratamento de Erro ---
def gerar_insight(summarizer, texto, nome_projeto):
    """Gera insight com tratamento robusto de erro"""
    try:
        # Dividir texto em chunks se for muito longo
        palavras = texto.split()
        max_palavras_chunk = 512
        
        if len(palavras) > max_palavras_chunk:
            # Processar em múltiplos chunks
            chunks = [
                " ".join(palavras[i:i+max_palavras_chunk]) 
                for i in range(0, len(palavras), max_palavras_chunk)
            ]
            resumos_chunks = []
            
            for chunk in chunks:
                try:
                    resultado = summarizer(
                        f"summarize: {chunk}",
                        max_length=150,
                        min_length=50,
                        do_sample=False
                    )
                    resumos_chunks.append(resultado[0]['summary_text'].strip())
                except Exception as e:
                    logger.warning(f"[AVISO] Erro ao processar chunk: {e}")
                    continue
            
            insight_texto = " ".join(resumos_chunks)
        else:
            # Processar texto inteiro
            insight_bruto = summarizer(
                f"summarize: {texto}",
                max_length=150,
                min_length=50,
                do_sample=False
            )
            insight_texto = insight_bruto[0]['summary_text'].strip()
        
        logger.info(f"[OK] Insight: '{nome_projeto}' -> {insight_texto[:80]}...")
        return insight_texto
        
    except Exception as e:
        logger.error(f"[ERRO] ao gerar insight para '{nome_projeto}': {e}")
        return None
    
    
# --- Funcao para Enriquecer Resumo ---
def enriquecer_resumo(resumo_ia, projeto):
    """Enriquece o resumo com contexto do projeto"""
    resumo_enriquecido = f"""
RESUMO EXECUTIVO - {projeto['nome_projeto']}
{'='*80}

{resumo_ia}

CONTEXTO DO PROJETO:
- Responsavel: {projeto.get('responsavel', 'N/A')}
- Status Atual: {projeto.get('status', 'N/A')}
- Ultima Atualizacao: {projeto.get('data_ultima_atualizacao', 'N/A')}

DESAFIOS PRINCIPAIS:
{projeto.get('principais_desafios', 'Nao informado')}

ACOES EM ANDAMENTO:
{projeto.get('acoes_corretivas', 'Nao informadas')}

PERSPECTIVA:
{projeto.get('perspectiva', 'Nao informada')}
"""
    return resumo_enriquecido.strip()

# --- Funcao de Processamento Principal Melhorada ---
def gerar_insights(atualizar_existentes=False):
    """
    Gera insights de IA para projetos
    
    Args:
        atualizar_existentes (bool): Se True, reprocessa projetos que ja tem insight
    """
    # Carregar modelo
    summarizer = carregar_modelo()
    if summarizer is None:
        return False
    
    # Conectar ao banco
    conexao = get_db_connection()
    if conexao is None:
        return False
    
    try:
        cursor = conexao.cursor()
        
        # Determinar query baseado no parametro
        if atualizar_existentes:
            query = """
                SELECT id, nome_projeto, resumo_executivo, principais_desafios 
                FROM projetos 
                WHERE (resumo_executivo IS NOT NULL OR principais_desafios IS NOT NULL)
                ORDER BY id DESC
            """
            logger.info("[MODO] Reprocessando TODOS os projetos...")
        else:
            query = """
                SELECT id, nome_projeto, resumo_executivo, principais_desafios 
                FROM projetos 
                WHERE resumo_ia IS NULL 
                AND (resumo_executivo IS NOT NULL OR principais_desafios IS NOT NULL)
                ORDER BY id DESC
            """
            logger.info("[MODO] Processando apenas novos projetos...")
        
        cursor.execute(query)
        projetos_para_processar = cursor.fetchall()
        
        if not projetos_para_processar:
            logger.info("[INFO] Nenhum projeto para processar. Banco atualizado.")
            return True
        
        logger.info(f"[INFO] Encontrados {len(projetos_para_processar)} projetos para processar")
        
        # Processamento em batch
        sucesso_count = 0
        erro_count = 0
        
        for idx, projeto in enumerate(projetos_para_processar, 1):
            logger.info(f"\n[{idx}/{len(projetos_para_processar)}] Processando: {projeto['nome_projeto']}")
            
            # Preparar texto
            texto = preparar_texto(projeto)
            if not texto:
                erro_count += 1
                continue
            
            # Gerar insight
            insight = gerar_insight(summarizer, texto, projeto['nome_projeto'])
            if not insight:
                erro_count += 1
                continue
            
            # Salvar no banco
            try:
                cursor.execute(
                    "UPDATE projetos SET resumo_ia = ?, data_processamento_ia = ? WHERE id = ?",
                    (insight, datetime.now().isoformat(), projeto['id'])
                )
                sucesso_count += 1
                
                # Commit a cada X projetos (melhor performance)
                if idx % BATCH_SIZE == 0:
                    conexao.commit()
                    logger.info(f"[OK] Batch salvo ({idx}/{len(projetos_para_processar)})")
                    
            except Exception as e:
                logger.error(f"[ERRO] ao salvar insight: {e}")
                erro_count += 1
        
        # Commit final
        conexao.commit()
        
        # Relatorio final
        logger.info("\n" + "="*60)
        logger.info("[RELATORIO] FINAL:")
        logger.info(f"[OK] Sucessos: {sucesso_count}")
        logger.info(f"[ERRO] Erros: {erro_count}")
        logger.info(f"[INFO] Taxa de sucesso: {(sucesso_count/len(projetos_para_processar)*100):.1f}%")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"[ERRO] critico durante processamento: {e}")
        if conexao:
            conexao.rollback()
        return False
        
    finally:
        if conexao:
            conexao.close()
            logger.info("[INFO] Conexao com banco fechada.")

# --- Funcao para Estatisticas ---
def mostrar_estatisticas():
    """Mostra estatisticas de processamento"""
    conexao = get_db_connection()
    if not conexao:
        return
    
    try:
        cursor = conexao.cursor()
        
        # Total de projetos
        cursor.execute("SELECT COUNT(*) as total FROM projetos")
        total = cursor.fetchone()['total']
        
        # Projetos com insight
        cursor.execute("SELECT COUNT(*) as com_insight FROM projetos WHERE resumo_ia IS NOT NULL")
        com_insight = cursor.fetchone()['com_insight']
        
        # Projetos sem insight
        sem_insight = total - com_insight
        
        logger.info("\n" + "="*60)
        logger.info("[ESTATISTICAS] DO BANCO:")
        logger.info(f"Total de projetos: {total}")
        logger.info(f"[OK] Com insight: {com_insight} ({(com_insight/total*100):.1f}%)")
        logger.info(f"[ERRO] Sem insight: {sem_insight} ({(sem_insight/total*100):.1f}%)")
        logger.info("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Erro ao obter estatisticas: {e}")
    finally:
        conexao.close()

# --- Main ---
if __name__ == "__main__":
    import sys
    
    # Criar pasta de logs se nao existir
    os.makedirs("logs", exist_ok=True)
    
    logger.info("[INICIO] INICIANDO PROCESSADOR DE IA SONAE")
    
    # Verificar argumentos
    atualizar = "--atualizar" in sys.argv
    
    if atualizar:
        logger.info("[AVISO] Flag --atualizar detectada: reprocessando TODOS os projetos")
    
    # Executar processamento
    sucesso = gerar_insights(atualizar_existentes=atualizar)
    
    if sucesso:
        # Mostrar estatisticas
        mostrar_estatisticas()
        logger.info("[OK] Processamento concluido com sucesso!")
        sys.exit(0)
    else:
        logger.error("[ERRO] Processamento falhou!")
        sys.exit(1)