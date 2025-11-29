import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from Auth.autenticacao import AuthManager

def render_login_page():
    """Renderiza a página de login"""
    
    # Espaçamento superior
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    # Centralizar conteúdo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo e título
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <div style="
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, #06b6d4, #7c3aed);
                border-radius: 20px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 700;
                font-size: 36px;
                margin-bottom: 1rem;
            ">MS</div>
            <h1 style="margin: 0.5rem 0;">Dashboard MC Sonae</h1>
            <p style="color: #64748b; font-size: 1.1rem;">Sistema de Gerenciamento de Projetos</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Formulário de login
        st.markdown("### Fazer Login")
        
        with st.form("login_form"):
            username = st.text_input(
                "Usuário",
                placeholder="Digite seu nome de usuário",
                key="login_username"
            )
            
            senha = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha",
                key="login_senha"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button(
                    "Entrar",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_btn2:
                cadastro = st.form_submit_button(
                    "Criar Conta",
                    use_container_width=True
                )
            
            if submit:
                if not username or not senha:
                    st.error("Por favor, preencha todos os campos!")
                else:
                    auth = AuthManager()
                    usuario = auth.verificar_login(username, senha)
                    
                    if usuario:
                        # Salvar dados do usuário na sessão
                        st.session_state.logged_in = True
                        st.session_state.user_id = usuario['id']
                        st.session_state.username = usuario['username']
                        st.session_state.email = usuario['email']
                        st.session_state.nome_completo = usuario['nome_completo']
                        st.session_state.cargo = usuario['cargo']
                        st.session_state.user_data = usuario
                        
                        # Buscar permissões
                        st.session_state.permissoes = auth.obter_permissoes_usuario(usuario['id'])
                        
                        st.success(f"Bem-vindo, {usuario['nome_completo']}!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos!")
            
            if cadastro:
                st.session_state.show_cadastro = True
                st.rerun()
        
        st.divider()
        
        # Informações adicionais
        with st.expander("Precisa de ajuda?"):
            st.markdown("""
            **Primeiro acesso?**
            - Clique em "Criar Conta" para solicitar acesso ao sistema
            - Sua solicitação será analisada por um administrador
            - Você receberá uma resposta por email
            
            **Esqueceu sua senha?**
            - Entre em contato com o administrador do sistema
            
            **Suporte:**
            - Email: admin@mcsonae.com
            """)


def verificar_autenticacao():
    """
    Verifica se o usuário está autenticado.
    Retorna True se estiver, False caso contrário.
    """
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    return st.session_state.logged_in


def logout():
    """Faz logout do usuário"""
    # Limpar dados da sessão
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.nome_completo = None
    st.session_state.cargo = None
    st.session_state.permissoes = []
    
    st.success("Logout realizado com sucesso!")
    st.rerun()


def tem_permissao(permissao: str) -> bool:
    """
    Verifica se o usuário logado tem determinada permissão.
    """
    if not verificar_autenticacao():
        return False
    
    permissoes = st.session_state.get('permissoes', [])
    return permissao in permissoes


def e_admin() -> bool:
    """Verifica se o usuário logado é admin"""
    if not verificar_autenticacao():
        return False
    
    return st.session_state.get('cargo') == 'admin'
