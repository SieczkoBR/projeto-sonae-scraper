import streamlit as st
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from Auth.autenticacao import AuthManager

def validar_email(email: str) -> bool:
    """Valida formato de email"""
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_senha(senha: str) -> tuple[bool, str]:
    """
    Valida força da senha.
    Retorna (válido, mensagem)
    """
    if len(senha) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    
    if not any(c.isupper() for c in senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
    
    if not any(c.islower() for c in senha):
        return False, "Senha deve conter pelo menos uma letra minúscula"
    
    if not any(c.isdigit() for c in senha):
        return False, "Senha deve conter pelo menos um número"
    
    return True, "Senha válida"

def render_cadastro_page():
    """Renderiza a página de cadastro de nova conta"""
    
    # Centralizar conteúdo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Botão voltar no topo
        if st.button("Voltar para Login", key="voltar_topo", type="secondary"):
            st.session_state.show_cadastro = False
            st.session_state.pop('cadastro_sucesso', None)
            st.rerun()
        
        st.markdown("---")
        
        # Logo e título
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #06b6d4, #7c3aed);
                border-radius: 15px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 700;
                font-size: 28px;
                margin-bottom: 0.5rem;
            ">MS</div>
            <h2 style="margin: 0.5rem 0;">Criar Nova Conta</h2>
            <p style="color: #64748b;">Preencha os dados para solicitar acesso</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Formulário de cadastro
        with st.form("cadastro_form"):
            st.markdown("### Dados Pessoais")
            
            nome_completo = st.text_input(
                "Nome Completo *",
                placeholder="Digite seu nome completo",
                key="cadastro_nome"
            )
            
            email = st.text_input(
                "Email *",
                placeholder="seu.email@mcsonae.com",
                key="cadastro_email",
                help="Use seu email corporativo"
            )
            
            username = st.text_input(
                "Nome de Usuário *",
                placeholder="Digite um nome de usuário único",
                key="cadastro_username",
                help="Será usado para fazer login"
            )
            
            st.divider()
            st.markdown("### Senha")
            
            senha = st.text_input(
                "Senha *",
                type="password",
                placeholder="Digite uma senha forte",
                key="cadastro_senha",
                help="Mínimo 6 caracteres, incluindo maiúscula, minúscula e número"
            )
            
            senha_confirm = st.text_input(
                "Confirmar Senha *",
                type="password",
                placeholder="Digite a senha novamente",
                key="cadastro_senha_confirm"
            )
            
            st.divider()
            st.markdown("### Cargo Solicitado")
            
            cargo = st.selectbox(
                "Selecione o cargo *",
                options=["visualizador", "analista", "gestor", "desenvolvedor"],
                format_func=lambda x: {
                    "visualizador": "Visualizador - Apenas visualização",
                    "analista": "Analista - Visualização e análises",
                    "gestor": "Gestor - Gerenciamento de projetos",
                    "desenvolvedor": "Desenvolvedor - Acesso técnico completo"
                }.get(x, x),
                key="cadastro_cargo",
                help="Sua solicitação será analisada pelo administrador"
            )
            
            st.divider()
            st.markdown("### Justificativa")
            
            justificativa = st.text_area(
                "Por que você precisa de acesso? *",
                placeholder="Explique brevemente o motivo da sua solicitação...",
                height=100,
                key="cadastro_justificativa",
                help="Esta informação ajudará o administrador a avaliar sua solicitação"
            )
            
            st.divider()
            
            termos = st.checkbox(
                "Li e aceito os termos de uso do sistema",
                key="cadastro_termos"
            )
            
            st.divider()
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button(
                    "Enviar Solicitação",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                cancelar = st.form_submit_button(
                    "Cancelar",
                    use_container_width=True
                )
        
        if cancelar:
            st.session_state.show_cadastro = False
            st.rerun()
        
        if submit:
            # Validações
            erros = []
            
            if not all([nome_completo, email, username, senha, senha_confirm, cargo, justificativa]):
                erros.append("Todos os campos obrigatórios (*) devem ser preenchidos")
            
            if email and not validar_email(email):
                erros.append("Email inválido")
            
            if senha and senha_confirm and senha != senha_confirm:
                erros.append("As senhas não coincidem")
            
            if senha:
                senha_valida, mensagem_senha = validar_senha(senha)
                if not senha_valida:
                    erros.append(mensagem_senha)
            
            if not termos:
                erros.append("Você deve aceitar os termos de uso")
            
            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                # Criar solicitação de conta
                auth = AuthManager()
                sucesso = auth.criar_solicitacao_conta(
                    username=username,
                    email=email,
                    senha=senha,
                    nome_completo=nome_completo,
                    cargo_solicitado=cargo,
                    mensagem_solicitacao=justificativa
                )
                
                if sucesso:
                    st.success("Solicitação enviada com sucesso!")
                    st.info("Aguarde a aprovação do administrador. Você receberá um email quando sua conta for aprovada.")
                    st.balloons()
                    
                    # Voltar para login após alguns segundos
                    import time
                    time.sleep(3)
                    st.session_state.show_cadastro = False
                    st.rerun()
                else:
                    st.error("Erro ao enviar solicitação. Username ou email já cadastrado, ou você já tem uma solicitação pendente.")
        
        st.divider()
        
        # Informações sobre cargos
        with st.expander("Informações sobre os cargos"):
            st.markdown("""
            **Visualizador**
            - Visualizar dashboard e relatórios
            - Acesso somente leitura
            
            **Analista**
            - Tudo do Visualizador
            - Gerar insights de IA
            - Criar relatórios personalizados
            
            **Gestor**
            - Tudo do Analista
            - Criar e gerenciar projetos
            - Editar informações de projetos
            
            **Desenvolvedor**
            - Tudo do Gestor
            - Acesso técnico ao sistema
            - Gerenciar configurações avançadas
            """)
