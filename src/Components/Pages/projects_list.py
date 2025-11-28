import streamlit as st
import pandas as pd
from datetime import datetime
from Components.Charts import get_status_info

def render_projects_list_page(df_filtrado):
    """Renderiza a página de Lista de Projetos"""
    st.title("📋 Lista Completa de Projetos")
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum projeto encontrado")
        return
    
    st.info(f"📊 Mostrando {len(df_filtrado)} projeto(s)")
    
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
