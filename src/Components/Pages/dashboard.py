import streamlit as st
from Components.Kpis import render_kpi_row
from Components.Charts import (
    criar_grafico_status,
    criar_timeline_projetos,
    criar_grafico_responsaveis
)

def render_dashboard_page(df_filtrado):
    """Renderiza a página do Dashboard Geral"""
    st.title("📊 Dashboard Geral de Projetos MC Sonae")
    st.markdown("Visão completa do portfólio de projetos")
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado.")
        return
    
    # KPIs
    render_kpi_row(df_filtrado)
    
    st.divider()
    
    # Gráficos lado a lado
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        fig_status = criar_grafico_status(df_filtrado)
        if fig_status:
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col_dir:
        fig_timeline = criar_timeline_projetos(df_filtrado)
        if fig_timeline:
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("📅 Sem dados de timeline disponíveis")
    
    st.divider()
    st.subheader("👥 Projetos por Responsável")
    
    fig_resp = criar_grafico_responsaveis(df_filtrado)
    if fig_resp:
        st.plotly_chart(fig_resp, use_container_width=True)
    else:
        st.info("Sem dados de responsáveis disponíveis")
