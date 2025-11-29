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
from Components.Pages.login import render_login_page, verificar_autenticacao
from Components.Pages.cadastro import render_cadastro_page
from Components.Pages.perfil import render_perfil_page
from Components.Pages.admin_usuarios import render_admin_usuarios_page
from Components.Pages.aprovacao_contas import render_aprovacao_contas_page
from Components.Pages.aprovacao_mudanca_cargo import render_aprovacao_mudanca_cargo_page
from Components.Pages.criar_projeto import render_criar_projeto_page
from Components.Pages.gerenciar_projetos import render_gerenciar_projetos_page

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

# --- VERIFICAR AUTENTICAÇÃO ---
if not verificar_autenticacao():
    # Verificar se deve mostrar página de cadastro
    if st.session_state.get('show_cadastro', False):
        render_cadastro_page()
    else:
        render_login_page()
else:
    # --- SIDEBAR ---
    pagina, df_filtrado = render_sidebar()

    # --- PÁGINAS ---
    if pagina == "Dashboard Geral":
        render_dashboard_page(df_filtrado)

    elif pagina == "Lista de Projetos":
        render_projects_list_page(df_filtrado)

    elif pagina == "Detalhes do Projeto":
        render_project_details_page(df_filtrado)

    elif pagina == "Insights de IA":
        render_ai_insights_page(df_filtrado)

    elif pagina == "Relatório Executivo IA":
        render_custom_summary_page()
    
    elif pagina == "Criar Projeto":
        render_criar_projeto_page()
    
    elif pagina == "Gerenciar Projetos":
        render_gerenciar_projetos_page()
    
    elif pagina == "Administrar Usuários":
        render_admin_usuarios_page()
    
    elif pagina == "Aprovar Contas":
        render_aprovacao_contas_page()
    
    elif pagina == "Aprovar Mudança de Cargo":
        render_aprovacao_mudanca_cargo_page()
    
    elif pagina == "Perfil":
        render_perfil_page()

    # --- Footer ---
    st.divider()
    components.html(render_footer(), height=150, scrolling=False)
