import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

# Adicionar path correto para importar Readers
caminho_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, caminho_src)

from Readers.criptograph import decriptar_dado
from Components.Pages.login import logout

def carregar_dados():
    """Carrega dados do banco SQLite e descriptografa campos sensíveis"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        df = pd.read_sql_query("SELECT * FROM projetos", conexao)
        conexao.close()
        
        # Descriptografar o campo 'responsavel' para exibição no frontend
        if 'responsavel' in df.columns and not df.empty:
            def descriptografar_seguro(valor):
                try:
                    if pd.notna(valor) and valor != '':
                        return decriptar_dado(valor)
                    return valor
                except Exception as e:
                    # Se não conseguir descriptografar, retorna o valor original
                    return valor
            
            df['responsavel'] = df['responsavel'].apply(descriptografar_seguro)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame()


def contar_solicitacoes_pendentes() -> int:
    """Conta o número de solicitações de conta pendentes"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM solicitacoes_conta WHERE status = 'pendente'")
        count = cursor.fetchone()[0]
        conexao.close()
        return count
    except:
        return 0


def contar_mudancas_cargo_pendentes() -> int:
    """Conta o número de solicitações de mudança de cargo pendentes"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM mudancas_cargo WHERE status = 'pendente'")
        count = cursor.fetchone()[0]
        conexao.close()
        return count
    except:
        return 0

def render_sidebar():
    """Renderiza a sidebar completa com navegação e filtros"""
    with st.sidebar:
        # Informações do usuário logado
        cargo = st.session_state.get('cargo', '')
        nome_completo = st.session_state.get('nome_completo', 'Usuário')
        username = st.session_state.get('username', '')
        
        # Card do usuário
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #06b6d4, #7c3aed);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            color: white;
        ">
            <div style="font-size: 0.9rem; opacity: 0.9;">Logado como:</div>
            <div style="font-weight: 700; font-size: 1.1rem; margin: 0.3rem 0;">{nome_completo}</div>
            <div style="font-size: 0.85rem; opacity: 0.8;">@{username}</div>
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 0.3rem 0.6rem;
                border-radius: 5px;
                display: inline-block;
                margin-top: 0.5rem;
                font-size: 0.8rem;
                font-weight: 600;
            ">{cargo.upper()}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navegação baseada no cargo
        st.title("Navegação")
        
        # Definir páginas por cargo
        paginas_por_cargo = {
            'admin': [
                "Administrar Usuários",
                "Aprovar Contas",
                "Aprovar Mudança de Cargo"
            ],
            'desenvolvedor': [
                "Dashboard Geral",
                "Lista de Projetos",
                "Detalhes do Projeto",
                "Insights de IA",
                "Relatório Automatizado",
                "Perfil"
            ],
            'gestor': [
                "Dashboard Geral",
                "Lista de Projetos",
                "Detalhes do Projeto",
                "Insights de IA",
                "Relatório Automatizado",
                "Criar Projeto",
                "Gerenciar Projetos",
                "Perfil"
            ],
            'analista': [
                "Dashboard Geral",
                "Lista de Projetos",
                "Detalhes do Projeto",
                "Insights de IA",
                "Perfil"
            ],
            'visualizador': [
                "Dashboard Geral",
                "Lista de Projetos",
                "Perfil"
            ]
        }
        
        # Obter páginas permitidas para o cargo
        paginas_permitidas = paginas_por_cargo.get(cargo, paginas_por_cargo['visualizador'])
        
        # Verificar notificações (apenas para admin)
        if cargo == 'admin':
            num_solicitacoes = contar_solicitacoes_pendentes()
            num_mudancas = contar_mudancas_cargo_pendentes()
            
            if num_solicitacoes > 0 or num_mudancas > 0:
                st.warning(f"Você tem {num_solicitacoes} solicitações de conta e {num_mudancas} solicitações de mudança de cargo pendentes!")
        
        pagina = st.radio(
            "Escolha uma página:",
            paginas_permitidas,
            key="pagina_radio"
        )
        
        st.divider()
        
        # Botão de atualizar com cor customizada
        st.markdown("""
        <style>
        div[data-testid="stButton"] button[kind="secondary"] {
            background-color: #06b6d4 !important;
            color: white !important;
            border: none !important;
        }
        div[data-testid="stButton"] button[kind="secondary"]:hover {
            background-color: #0891b2 !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("Atualizar Dados", type="secondary", width="stretch", key="refresh_btn"):
            st.cache_data.clear()
            st.rerun()
        
        # Botão de sair no final com cor customizada
        st.markdown("""
        <style>
        div[data-testid="stButton"] button[kind="primary"] {
            background-color: #dc2626 !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            background-color: #b91c1c !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("Sair do Sistema", type="primary", width="stretch", key="logout_bottom_btn"):
            logout()
        
        df_projetos = carregar_dados()
        
        return pagina, df_projetos
