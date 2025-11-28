import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

# Adicionar path correto para importar Readers
caminho_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, caminho_src)

from Readers.criptograph import decriptar_dado
from Components.Filters import render_sidebar_filters, render_refresh_button

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
        st.error(f"❌ Erro ao carregar dados: {e}")
        import traceback
        st.error(traceback.format_exc())
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
