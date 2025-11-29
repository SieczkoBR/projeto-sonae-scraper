import streamlit as st
import pandas as pd
from datetime import datetime
from Components.Charts import get_status_info

def render_projects_list_page(df_projetos):
    """Renderiza a página de Lista de Projetos"""
    st.title("Lista Completa de Projetos")
    
    if df_projetos.empty:
        st.warning("Nenhum projeto encontrado")
        return
    
    # Filtros
    st.subheader("Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_opcoes = ["Todos"] + sorted(df_projetos['status'].dropna().unique().tolist())
        filtro_status = st.selectbox("Status", status_opcoes, key="filtro_status_list")
    
    with col2:
        responsavel_opcoes = ["Todos"] + sorted(df_projetos['responsavel'].dropna().unique().tolist())
        filtro_responsavel = st.selectbox("Responsável", responsavel_opcoes, key="filtro_resp_list")
    
    with col3:
        busca = st.text_input("Buscar projeto", placeholder="Digite o nome...", key="busca_list")
    
    # Aplicar filtros
    df_filtrado = df_projetos.copy()
    
    if filtro_status != "Todos":
        df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
    
    if filtro_responsavel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['responsavel'] == filtro_responsavel]
    
    if busca:
        df_filtrado = df_filtrado[
            df_filtrado['nome'].str.contains(busca, case=False, na=False) |
            df_filtrado['nome_projeto'].str.contains(busca, case=False, na=False)
        ]
    
    if df_filtrado.empty:
        st.warning("Nenhum projeto encontrado com os filtros selecionados")
        return
    
    st.divider()
    
    st.info(f"Mostrando {len(df_filtrado)} projeto(s)")
    
    # Criar coluna de status visual
    df_display = df_filtrado.copy()
    df_display['Status Visual'] = df_display['status'].apply(
        lambda x: get_status_info(x)[0] + " " + get_status_info(x)[2]
    )
    
    # Configuração das colunas
    colunas_exibir = ['nome_projeto', 'Status Visual', 'responsavel', 'data_ultima_atualizacao']
    colunas_disponiveis = [col for col in colunas_exibir if col in df_display.columns]
    
    config_colunas = {
        "nome_projeto": st.column_config.TextColumn("📁 Projeto", width="large"),
        "Status Visual": st.column_config.TextColumn("🎯 Status", width="medium"),
        "responsavel": st.column_config.TextColumn("👤 Responsável", width="medium"),
        "data_ultima_atualizacao": st.column_config.TextColumn("📅 Última Atualização", width="medium")
    }
    
    st.dataframe(
        df_display[colunas_disponiveis],
        column_config=config_colunas,
        hide_index=True,
        use_container_width=True,
        height=600
    )
    
    # Botão para baixar dados
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados como CSV",
        data=csv,
        file_name=f"projetos_sonae_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
