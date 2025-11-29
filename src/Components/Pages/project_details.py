import streamlit as st
from Components.Charts import get_status_info

def render_project_details_page(df_projetos):
    """Renderiza a página de Detalhes do Projeto"""
    st.title("Detalhes Completos do Projeto")
    
    if df_projetos.empty:
        st.warning("Nenhum projeto disponível")
        return
    
    # Seletor de projeto
    projeto_selecionado = st.selectbox(
        "Selecione um projeto:",
        df_projetos['nome_projeto'].tolist(),
        index=0
    )
    
    # Filtrar dados do projeto
    projeto = df_projetos[df_projetos['nome_projeto'] == projeto_selecionado].iloc[0]
    
    # Header com status
    col_nome, col_status = st.columns([3, 1])
    
    with col_nome:
        st.header(projeto['nome_projeto'])
    
    with col_status:
        icone, cor, texto = get_status_info(projeto['status'])
        st.markdown(f"### {icone} {texto}")
    
    st.divider()
    
    # Informações básicas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Responsável", projeto.get('responsavel', 'N/A'))
    
    with col2:
        st.metric("Última Atualização", projeto.get('data_ultima_atualizacao', 'N/A'))
    
    with col3:
        st.metric("Fonte", projeto.get('fonte_dados', 'N/A').split('/')[-1] if projeto.get('fonte_dados') else 'N/A')
    
    st.divider()
    
    # Abas para conteúdo detalhado
    tabs = st.tabs(["Resumo Executivo", "Progresso", "Desafios", "Ações", "Perspectiva", "Insight IA"])
    
    with tabs[0]:
        if projeto.get('resumo_executivo'):
            st.markdown(projeto['resumo_executivo'])
        else:
            st.info("Sem resumo executivo disponível")
    
    with tabs[1]:
        if projeto.get('progresso_atual'):
            st.markdown(projeto['progresso_atual'])
        else:
            st.info("Sem informações de progresso disponíveis")
    
    with tabs[2]:
        if projeto.get('principais_desafios'):
            st.markdown(projeto['principais_desafios'])
        else:
            st.info("Sem desafios registrados")
    
    with tabs[3]:
        if projeto.get('acoes_corretivas'):
            st.markdown(projeto['acoes_corretivas'])
        else:
            st.info("Sem ações corretivas registradas")
    
    with tabs[4]:
        if projeto.get('perspectiva'):
            st.markdown(projeto['perspectiva'])
        else:
            st.info("Sem perspectiva disponível")
    
    with tabs[5]:
        if projeto.get('resumo_ia'):
            st.success(f"**Insight Automático:** {projeto['resumo_ia']}")
        else:
            st.warning("Insight de IA ainda não gerado. Execute `processador_ia.py`")
