import streamlit as st
import pandas as pd
import sqlite3
import os

# --- Configuração da Página (Sem mudanças) ---
st.set_page_config(
    page_title="Dashboard de Projetos MC Sonae",
    page_icon="📊",
    layout="wide"
)

# --- Constantes (Sem mudanças) ---
CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")

# --- Função para Carregar Dados (Sem mudanças) ---
@st.cache_data
def carregar_dados():
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        df = pd.read_sql_query("SELECT * FROM projetos", conexao)
        conexao.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}")
        return pd.DataFrame()

# --- NOVA FUNÇÃO: Mapear Status para Ícones (Rumo ao Figma!) ---
def get_status_visual(status):
    """Traduz o texto do status em um ícone com cor."""
    status_lower = str(status).lower() # Normaliza o texto
    
    if "atrasado" in status_lower:
        return "🔴 Atrasado"
    elif "concluído" in status_lower or "concluido" in status_lower:
        return "🟢 Concluído"
    elif "em andamento" in status_lower:
        return "🟡 Em Andamento"
    elif "no prazo" in status_lower:
        return "🔵 No Prazo"
    else:
        # Caso padrão para status não mapeados
        return "⚪️ " + str(status)

# --- Construção da Página ---
st.title("📊 Dashboard Geral de Projetos")
st.markdown("Bem-vindo ao painel de acompanhamento de projetos da MC Sonae.")

# Carrega os dados
df_projetos = carregar_dados()

# Removemos a seção de "Debug"
# st.subheader("Debug: Dados Brutos do Banco")
# st.write(df_projetos)

if df_projetos.empty:
    st.warning("Nenhum dado encontrado no banco de dados.")
else:
    # --- Seção: Lista de Projetos (AGORA COM st.data_editor) ---
    st.header("Lista de Projetos")
    
    # 1. Criamos a nova coluna visual aplicando nossa função
    # Criamos uma cópia para não mexer nos dados em cache
    df_display = df_projetos.copy()
    df_display['status_visual'] = df_display['status'].apply(get_status_visual)
    
    # 2. Definimos a configuração das colunas
    # Isso nos permite renomear, reordenar e esconder colunas
    configuracao_colunas = {
        "nome_projeto": st.column_config.TextColumn(
            label="Nome do Projeto", # Texto do cabeçalho
            width="large" # Faz a coluna do nome ser a maior
        ),
        "status_visual": st.column_config.TextColumn(
            label="Status" # Renomeia nossa coluna de ícone para "Status"
        ),
        "data_ultima_atualizacao": st.column_config.TextColumn(
            label="Última Atualização"
        ),
        "responsavel": st.column_config.TextColumn(
            label="Responsável"
        ),
        
        # --- Escondendo colunas que não queremos ver ---
        "id": None, # "None" esconde a coluna
        "status": None, # Esconde o "status" original (só queremos o visual)
        "resumo_ia": None,
        "fonte_dados": None
    }
    
    # 3. Exibimos a tabela com o st.data_editor
    st.data_editor(
        df_display,
        column_config=configuracao_colunas,
        width="stretch", # Para usar toda a largura
        hide_index=True, # Esconde o índice (0, 1, 2...)
        disabled=True # Desabilita a edição (torna "read-only")
    )