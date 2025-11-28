import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Importar componentes
from Components.Footer import render_footer
from Components.Sidebar import render_sidebar
from Components.Pages import (
    render_dashboard_page,
    render_projects_list_page,
    render_project_details_page,
    render_ai_insights_page,
    render_custom_summary_page
)

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard MC Sonae",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS ---
css_path = Path(__file__).parent / "Styles/styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
else:
    st.warning("Arquivo de estilos não encontrado: src/Styles/styles.css")

else:
    st.warning("Arquivo de estilos não encontrado: src/Styles/styles.css")

# --- SIDEBAR ---
pagina, df_filtrado = render_sidebar()

# --- PÁGINAS ---
if pagina == "📊 Dashboard Geral":
    render_dashboard_page(df_filtrado)

elif pagina == "📋 Lista de Projetos":
    render_projects_list_page(df_filtrado)

elif pagina == "🔍 Detalhes do Projeto":
    render_project_details_page(df_filtrado)

elif pagina == "🤖 Insights de IA":
    render_ai_insights_page(df_filtrado)

elif pagina == "📄 Criar Resumo Personalizado":
    render_custom_summary_page()

# --- Footer ---
st.divider()
components.html(render_footer(), height=150, scrolling=False)
