import streamlit as st

def render_sidebar_filters(df_projetos):
    """Renderiza filtros da sidebar"""
    if df_projetos.empty:
        st.warning("Sem dados para filtrar")
        return df_projetos.copy()
    
    # Filtro por status
    status_unicos = ["Todos"] + sorted(df_projetos['status'].dropna().unique().tolist())
    filtro_status = st.selectbox(
        "Status:", 
        status_unicos,
        key="filtro_status"
    )
    
    # Filtro por responsável
    responsaveis = ["Todos"] + sorted(df_projetos['responsavel'].dropna().unique().tolist())
    filtro_responsavel = st.selectbox(
        "Responsável:", 
        responsaveis,
        key="filtro_responsavel"
    )
    
    # Aplicar filtros
    df_filtrado = df_projetos.copy()
    
    if filtro_status != "Todos":
        df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
    
    if filtro_responsavel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['responsavel'] == filtro_responsavel]
    
    return df_filtrado

def render_refresh_button():
    """Renderiza botão de atualização de dados com estilo customizado"""
    if st.button(
        "Atualizar Dados", 
        use_container_width=True,
        key="refresh_button"
    ):
        st.cache_data.clear()
        st.success("Dados atualizados com sucesso!")
        st.rerun()
