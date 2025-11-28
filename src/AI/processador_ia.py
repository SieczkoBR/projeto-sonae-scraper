import sqlite3
import os
import re
import logging

# --- Configuração ---
CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "ia_processing.log")),
        logging.StreamHandler()
    ]
)


def extrair_conceitos_chave(texto, max_conceitos=3):
    """
    Extrai os conceitos-chave mais importantes de um texto.
    
    Args:
        texto: Texto para análise
        max_conceitos: Número máximo de conceitos a extrair
        
    Returns:
        list: Lista de conceitos-chave
    """
    # Palavras-chave técnicas relevantes
    palavras_relevantes = [
        'dados', 'análise', 'integração', 'riscos', 'gestão', 'monitoramento',
        'indicadores', 'desempenho', 'automação', 'ETL', 'API', 'dashboard',
        'relatórios', 'métricas', 'qualidade', 'consistência', 'alertas',
        'governança', 'compliance', 'estratégia', 'otimização', 'processos',
        'eficiência', 'performance', 'confiabilidade', 'segurança'
    ]
    
    texto_lower = texto.lower()
    conceitos_encontrados = []
    
    for palavra in palavras_relevantes:
        if palavra in texto_lower and palavra not in conceitos_encontrados:
            conceitos_encontrados.append(palavra)
            if len(conceitos_encontrados) >= max_conceitos:
                break
    
    return conceitos_encontrados


def extrair_frase_principal(texto):
    """
    Extrai a primeira frase significativa do texto.
    
    Args:
        texto: Texto para análise
        
    Returns:
        str: Primeira frase relevante
    """
    # Dividir em frases
    frases = re.split(r'[.!?]\s+', texto)
    
    # Retornar a primeira frase com mais de 20 caracteres
    for frase in frases:
        if len(frase.strip()) > 20:
            return frase.strip()
    
    return texto[:150].strip()


def gerar_insight_estruturado(texto_resumo, texto_desafios):
    """
    Gera um insight estruturado com gramática perfeita usando templates e extração de conceitos.
    
    Args:
        texto_resumo: Texto do resumo executivo
        texto_desafios: Texto dos principais desafios
        
    Returns:
        str: Insight gerado com gramática correta
    """
    try:
        # Extrair conceitos-chave do resumo
        conceitos_resumo = extrair_conceitos_chave(texto_resumo, max_conceitos=3)
        
        # Extrair conceitos-chave dos desafios
        conceitos_desafios = extrair_conceitos_chave(texto_desafios, max_conceitos=2)
        
        # Extrair frase principal do resumo
        frase_principal = extrair_frase_principal(texto_resumo)
        
        # Construir insight estruturado
        partes_insight = []
        
        # Parte 1: Foco principal
        if conceitos_resumo:
            if len(conceitos_resumo) == 1:
                conceitos_str = conceitos_resumo[0]
            elif len(conceitos_resumo) == 2:
                conceitos_str = f"{conceitos_resumo[0]} e {conceitos_resumo[1]}"
            else:
                conceitos_str = ", ".join(conceitos_resumo[:-1]) + f" e {conceitos_resumo[-1]}"
            
            partes_insight.append(f"Projeto focado em {conceitos_str}")
        else:
            # Usar frase principal como fallback
            partes_insight.append(frase_principal[:100])
        
        # Parte 2: Desafios principais
        if conceitos_desafios:
            if len(conceitos_desafios) == 1:
                desafios_str = conceitos_desafios[0]
            else:
                desafios_str = f"{conceitos_desafios[0]} e {conceitos_desafios[1]}"
            
            partes_insight.append(f"com desafios relacionados a {desafios_str}")
        
        # Parte 3: Objetivo estratégico (baseado no contexto)
        if 'dados' in conceitos_resumo or 'análise' in conceitos_resumo:
            partes_insight.append("visando suporte à tomada de decisão estratégica")
        elif 'riscos' in conceitos_resumo or 'gestão' in conceitos_resumo:
            partes_insight.append("para garantir operações seguras e eficientes")
        elif 'indicadores' in conceitos_resumo or 'monitoramento' in conceitos_resumo:
            partes_insight.append("permitindo acompanhamento contínuo de resultados e performance")
        elif 'automação' in conceitos_resumo or 'processos' in conceitos_resumo:
            partes_insight.append("otimizando processos e aumentando a eficiência operacional")
        
        # Combinar todas as partes
        insight = ", ".join(partes_insight) + "."
        
        # Garantir primeira letra maiúscula
        insight = insight[0].upper() + insight[1:]
        
        return insight
        
    except Exception as e:
        logging.error(f"Erro ao gerar insight estruturado: {str(e)}")
        return "Insight não disponível no momento."

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
def gerar_insight_para_projeto(projeto_id=None, texto_resumo=None, texto_desafios=None):
    """
    Gera insight estruturado para um projeto específico
    
    Args:
        projeto_id: ID do projeto (se fornecido, busca do banco)
        texto_resumo: Texto do resumo executivo (opcional)
        texto_desafios: Texto dos desafios (opcional)
    
    Returns:
        String com o insight gerado ou None se falhar
    """
    # Se projeto_id foi fornecido, buscar do banco
    if projeto_id:
        conexao = get_db_connection()
        if conexao is None:
            return None
        
        try:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT resumo_executivo, principais_desafios 
                FROM projetos WHERE id = ?
            """, (projeto_id,))
            
            projeto = cursor.fetchone()
            if projeto:
                texto_resumo = projeto['resumo_executivo']
                texto_desafios = projeto['principais_desafios']
        finally:
            conexao.close()
    
    # Verificar se temos texto para processar
    if not texto_resumo and not texto_desafios:
        logging.warning("Nenhum texto disponível para gerar insight")
        return None
    
    # Usar valores padrão se algum estiver vazio
    if not texto_resumo:
        texto_resumo = "Projeto em desenvolvimento"
    if not texto_desafios:
        texto_desafios = "Sem desafios registrados"
    
    try:
        # Gerar insight estruturado
        insight_texto = gerar_insight_estruturado(texto_resumo, texto_desafios)
        logging.info(f"Insight gerado: {insight_texto}")
        
        # Se projeto_id foi fornecido, salvar no banco
        if projeto_id:
            conexao = get_db_connection()
            if conexao:
                try:
                    cursor = conexao.cursor()
                    cursor.execute(
                        "UPDATE projetos SET resumo_ia = ? WHERE id = ?",
                        (insight_texto, projeto_id)
                    )
                    conexao.commit()
                    logging.info(f"Insight salvo para projeto ID {projeto_id}")
                finally:
                    conexao.close()
        
        return insight_texto
        
    except Exception as e:
        logging.error(f"Erro ao gerar insight: {e}")
        return None

def gerar_insights():
    """Processa todos os projetos sem insights de IA"""
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
            insight_texto = gerar_insight_para_projeto(
                projeto_id=projeto['id'],
                texto_resumo=projeto['resumo_executivo'],
                texto_desafios=projeto['principais_desafios']
            )
            
            if insight_texto:
                print(f"Insight gerado para '{projeto['nome_projeto']}': {insight_texto}")

        conexao.commit()
        print(f"Sucesso! {len(projetos_para_processar)} projetos atualizados com insights.")

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