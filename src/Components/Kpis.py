import streamlit as st
import pandas as pd

def render_kpi_row(df):
    """Renderiza a linha de KPIs do dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    total_projetos = len(df)
    concluidos = len(df[df['status'].str.contains('concluído|concluido', case=False, na=False)])
    em_andamento = len(df[df['status'].str.contains('andamento', case=False, na=False)])
    atrasados = len(df[df['status'].str.contains('atrasado|crítico', case=False, na=False)])
    
    with col1:
        st.metric("Total de Projetos", total_projetos, delta=None)
    
    with col2:
        st.metric("Concluídos", concluidos, delta=f"{(concluidos/total_projetos*100):.0f}%" if total_projetos > 0 else "0%")
    
    with col3:
        st.metric("Em Andamento", em_andamento, delta=None)
    
    with col4:
        st.metric("Atrasados", atrasados, delta=f"-{atrasados}" if atrasados > 0 else "0", delta_color="inverse")
