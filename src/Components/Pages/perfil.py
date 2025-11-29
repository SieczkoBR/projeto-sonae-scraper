import streamlit as st
from Auth.autenticacao import AuthManager
import re

def validar_senha(senha: str) -> tuple[bool, str]:
    """Valida requisitos da senha"""
    if len(senha) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    if not re.search(r'[A-Z]', senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
    if not re.search(r'[a-z]', senha):
        return False, "Senha deve conter pelo menos uma letra minúscula"
    if not re.search(r'\d', senha):
        return False, "Senha deve conter pelo menos um número"
    return True, "Senha válida"

def render_perfil_page():
    """Página de perfil do usuário"""
    st.title("Meu Perfil")
    
    user_data = st.session_state.get('user_data', {})
    
    if not user_data:
        st.error("Erro ao carregar dados do usuário")
        return
    
    # Informações do usuário
    st.subheader("Informações da Conta")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Nome Completo:** {user_data.get('nome_completo', 'N/A')}")
        st.info(f"**Email:** {user_data.get('email', 'N/A')}")
    
    with col2:
        st.info(f"**Nome de Usuário:** @{user_data.get('username', 'N/A')}")
        st.info(f"**Cargo:** {user_data.get('cargo', 'N/A').upper()}")
    
    # Informações adicionais
    if user_data.get('data_criacao'):
        st.text(f"Conta criada em: {user_data['data_criacao']}")
    
    if user_data.get('data_ultima_atividade'):
        st.text(f"Última atividade: {user_data['data_ultima_atividade']}")
    
    st.divider()
    
    # Alterar senha
    st.subheader("Alterar Senha")
    
    with st.form("form_alterar_senha"):
        senha_atual = st.text_input("Senha Atual *", type="password", help="Digite sua senha atual")
        senha_nova = st.text_input("Nova Senha *", type="password", help="Mínimo 6 caracteres com maiúscula, minúscula e número")
        senha_nova_confirmacao = st.text_input("Confirmar Nova Senha *", type="password", help="Digite a nova senha novamente")
        
        col_s, col_c = st.columns([2, 1])
        
        with col_s:
            submit = st.form_submit_button("Alterar Senha", type="primary", width="stretch")
        
        with col_c:
            cancel = st.form_submit_button("Cancelar", width="stretch")
    
    if cancel:
        st.info("Operação cancelada")
    
    if submit:
        if not senha_atual or not senha_nova or not senha_nova_confirmacao:
            st.error("Preencha todos os campos")
        elif senha_nova != senha_nova_confirmacao:
            st.error("As senhas não coincidem")
        else:
            valida, msg = validar_senha(senha_nova)
            if not valida:
                st.error(msg)
            else:
                auth_manager = AuthManager()
                sucesso, mensagem = auth_manager.alterar_senha(
                    user_data['id'],
                    senha_atual,
                    senha_nova
                )
                
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)
    
    st.divider()
    
    # Solicitar mudança de cargo
    cargo_atual = user_data.get('cargo', '')
    
    if cargo_atual != 'admin':
        st.subheader("Solicitar Mudança de Cargo")
        
        st.info("Se você precisa de permissões adicionais, solicite uma mudança de cargo. Um administrador analisará sua solicitação.")
        
        cargos_disponiveis = {
            'visualizador': 'Visualizador - Apenas visualização',
            'analista': 'Analista - Visualização e análises',
            'gestor': 'Gestor - Gerenciamento de projetos',
            'desenvolvedor': 'Desenvolvedor - Acesso técnico completo'
        }
        
        # Remover cargo atual da lista
        if cargo_atual in cargos_disponiveis:
            del cargos_disponiveis[cargo_atual]
        
        with st.form("form_mudanca_cargo"):
            cargo_solicitado = st.selectbox(
                "Cargo Desejado",
                options=list(cargos_disponiveis.keys()),
                format_func=lambda x: cargos_disponiveis.get(x, x)
            )
            
            justificativa = st.text_area(
                "Justificativa *",
                placeholder="Explique por que você precisa deste cargo...",
                height=100,
                help="Descreva as atividades que você precisa realizar"
            )
            
            submit_cargo = st.form_submit_button("Enviar Solicitação", type="primary", width="stretch")
        
        if submit_cargo:
            if not justificativa:
                st.error("A justificativa é obrigatória")
            else:
                auth_manager = AuthManager()
                
                if auth_manager.solicitar_mudanca_cargo(
                    user_data['id'],
                    cargo_solicitado,
                    justificativa
                ):
                    st.success("Solicitação enviada com sucesso! Aguarde a análise do administrador.")
                    st.info("Você receberá uma notificação quando sua solicitação for processada.")
                else:
                    st.error("Erro ao enviar solicitação. Você pode já ter uma solicitação pendente.")
