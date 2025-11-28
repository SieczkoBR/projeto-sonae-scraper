import streamlit as st
from Components.Charts import get_status_info

def render_ai_insights_page(df_filtrado):
    """Renderiza a página de Insights de IA"""
    st.title("🤖 Insights Gerados por IA")
    st.markdown("Resumos automáticos gerados pelo modelo T5")
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum projeto disponível")
        return
    
    # Filtrar apenas projetos com IA
    df_com_ia = df_filtrado[df_filtrado['resumo_ia'].notna()]
    
    if df_com_ia.empty:
        st.info("🤖 Nenhum insight de IA foi gerado ainda. Execute `python src/processador_ia.py`")
        return
    
    st.success(f"✅ {len(df_com_ia)} projeto(s) com insights de IA")
    
    for idx, projeto in df_com_ia.iterrows():
        with st.expander(f"🔍 {projeto['nome_projeto']}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**🤖 Insight Automático:**")
                st.info(projeto['resumo_ia'])
            
            with col2:
                icone, cor, texto = get_status_info(projeto['status'])
                st.markdown(f"**Status:** {icone} {texto}")
                st.markdown(f"**Responsável:** {projeto.get('responsavel', 'N/A')}")
