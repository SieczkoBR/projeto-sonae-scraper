import streamlit as st
import pandas as pd
import plotly.express as px

def get_status_info(status):
    """Retorna ícone, cor e texto do status"""
    status_lower = str(status).lower()
    
    if "atrasado" in status_lower or "crítico" in status_lower:
        return "🔴", "#ef4444", "Atrasado"
    elif "concluído" in status_lower or "concluido" in status_lower:
        return "🟢", "#10b981", "Concluído"
    elif "em andamento" in status_lower or "andamento" in status_lower:
        return "🟡", "#f59e0b", "Em Andamento"
    elif "no prazo" in status_lower:
        return "🔵", "#3b82f6", "No Prazo"
    else:
        return "⚪️", "#6b7280", str(status)

def criar_grafico_status(df):
    """Cria gráfico de pizza para distribuição de status"""
    if df.empty:
        return None
    
    df_viz = df.copy()
    df_viz['status_normalizado'] = df_viz['status'].apply(lambda x: get_status_info(x)[2])
    
    status_counts = df_viz['status_normalizado'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Distribuição de Status dos Projetos",
        color_discrete_map={
            "Concluído": "#10b981",
            "Em Andamento": "#f59e0b",
            "Atrasado": "#ef4444",
            "No Prazo": "#3b82f6"
        },
        hole=0.4
    )
    
    fig.update_layout(
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_timeline_projetos(df):
    """Cria linha do tempo dos projetos"""
    if df.empty or 'data_ultima_atualizacao' not in df.columns:
        return None
    
    df_timeline = df.copy()
    df_timeline['data_ultima_atualizacao'] = pd.to_datetime(
        df_timeline['data_ultima_atualizacao'], 
        errors='coerce'
    )
    
    df_timeline = df_timeline.dropna(subset=['data_ultima_atualizacao'])
    df_timeline = df_timeline.sort_values('data_ultima_atualizacao')
    
    if df_timeline.empty:
        return None
    
    fig = px.scatter(
        df_timeline,
        x='data_ultima_atualizacao',
        y='nome_projeto',
        color='status',
        title="Linha do Tempo das Atualizações",
        labels={'data_ultima_atualizacao': 'Data', 'nome_projeto': 'Projeto'},
        height=400
    )
    
    fig.update_traces(marker=dict(size=12))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    )
    
    return fig

def criar_grafico_responsaveis(df):
    """Cria gráfico de projetos por responsável"""
    if df.empty or 'responsavel' not in df.columns:
        return None
    
    responsavel_counts = df['responsavel'].value_counts().head(10)
    
    fig = px.bar(
        x=responsavel_counts.values,
        y=responsavel_counts.index,
        orientation='h',
        title="Top 10 Responsáveis",
        labels={'x': 'Número de Projetos', 'y': 'Responsável'},
        color=responsavel_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig