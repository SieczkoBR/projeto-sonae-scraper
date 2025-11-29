import streamlit as st
from Auth.autenticacao import AuthManager

def render_aprovacao_contas_page():
    """Página para aprovar/negar solicitações de conta"""
    st.title("Aprovar Solicitações de Conta")
    
    cargo = st.session_state.get('cargo', '')
    
    if cargo != 'admin':
        st.error("Acesso negado! Apenas administradores podem acessar esta página.")
        return
    
    auth = AuthManager()
    solicitacoes = auth.listar_solicitacoes_pendentes()
    
    if not solicitacoes:
        st.success("Não há solicitações pendentes no momento!")
        return
    
    st.info(f"Você tem **{len(solicitacoes)}** solicitações pendentes")
    
    for sol in solicitacoes:
        with st.expander(f"{sol['nome_completo']} (@{sol['username']})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Informações:**")
                st.text(f"Email: {sol['email']}")
                st.text(f"Cargo solicitado: {sol['cargo_solicitado'].upper()}")
                st.text(f"Data: {sol['data_solicitacao']}")
                
                if sol.get('justificativa'):
                    st.markdown("**Justificativa:**")
                    st.write(sol['justificativa'])
            
            with col2:
                st.markdown("**Ações:**")
                
                if st.button(f"Aprovar", key=f"aprovar_{sol['id']}", type="primary"):
                    sucesso = auth.aprovar_solicitacao(
                        sol['id'],
                        st.session_state.get('user_id'),
                        sol['cargo_solicitado']
                    )
                    
                    if sucesso:
                        st.success("Conta aprovada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao aprovar solicitação")
                
                if st.button(f"Negar", key=f"negar_{sol['id']}"):
                    sucesso = auth.negar_solicitacao(
                        sol['id'],
                        st.session_state.get('user_id')
                    )
                    
                    if sucesso:
                        st.success("Solicitação negada")
                        st.rerun()
                    else:
                        st.error("Erro ao negar solicitação")
