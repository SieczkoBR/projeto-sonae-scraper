import streamlit as st
import pandas as pd
import sqlite3
import os

from Components.Filters import render_sidebar_filters, render_refresh_button

def carregar_dados():
    """Carrega dados do banco SQLite (cópia local para evitar circular imports)"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        df = pd.read_sql_query("SELECT * FROM projetos", conexao)
        conexao.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

def render_sidebar():
    """Renderiza a sidebar completa com navegação e filtros"""
    with st.sidebar:
        st.title("🎯 Navegação")
        
        pagina = st.radio(
            "Escolha uma página:",
            [
                "📊 Dashboard Geral",
                "📋 Lista de Projetos",
                "🔍 Detalhes do Projeto",
                "🤖 Insights de IA",
                "📄 Criar Resumo Personalizado"
            ],
            key="pagina_radio"  # Key único para evitar duplicatas
        )
        
        st.divider()
        st.subheader("🔍 Filtros")
        
        df_projetos = carregar_dados()
        df_filtrado = render_sidebar_filters(df_projetos)
        
        st.divider()
        render_refresh_button()
        
        return pagina, df_filtrado