import streamlit as st
import sqlite3
import os

def render_admin_usuarios_page():
    """Página para admin gerenciar usuários"""
    st.title("Administrar Usuários")
    
    cargo = st.session_state.get('cargo', '')
    
    if cargo != 'admin':
        st.error("Acesso negado! Apenas administradores podem acessar esta página.")
        return
    
    usuarios = listar_usuarios()
    
    if not usuarios:
        st.info("Nenhum usuário encontrado no sistema")
        return
    
    st.subheader(f"Total de Usuários: {len(usuarios)}")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_cargo = st.selectbox(
            "Filtrar por Cargo",
            ["Todos", "admin", "desenvolvedor", "gestor", "analista", "visualizador"]
        )
    
    with col2:
        filtro_status = st.selectbox(
            "Filtrar por Status",
            ["Todos", "Ativos", "Inativos"]
        )
    
    with col3:
        busca = st.text_input("Buscar por nome/email", placeholder="Digite para buscar...")
    
    # Aplicar filtros
    usuarios_filtrados = usuarios
    
    if filtro_cargo != "Todos":
        usuarios_filtrados = [u for u in usuarios_filtrados if u.get('cargo') == filtro_cargo]
    
    if filtro_status == "Ativos":
        usuarios_filtrados = [u for u in usuarios_filtrados if u.get('ativo') == 1]
    elif filtro_status == "Inativos":
        usuarios_filtrados = [u for u in usuarios_filtrados if u.get('ativo') == 0]
    
    if busca:
        usuarios_filtrados = [
            u for u in usuarios_filtrados
            if busca.lower() in u.get('nome_completo', '').lower() or
               busca.lower() in u.get('email', '').lower() or
               busca.lower() in u.get('username', '').lower()
        ]
    
    st.divider()
    
    # Lista de usuários
    st.subheader(f"Usuários Encontrados: {len(usuarios_filtrados)}")
    
    for user in usuarios_filtrados:
        with st.expander(f"{user.get('nome_completo', 'N/A')} (@{user.get('username', 'N/A')})"):
            col_info, col_actions = st.columns([2, 1])
            
            with col_info:
                st.markdown("**Informações:**")
                st.text(f"ID: {user.get('id')}")
                st.text(f"Email: {user.get('email', 'N/A')}")
                st.text(f"Cargo: {user.get('cargo', 'N/A').upper()}")
                st.text(f"Status: {'Ativo' if user.get('ativo') else 'Inativo'}")
                
                if user.get('data_criacao'):
                    st.text(f"Criado em: {user['data_criacao']}")
                
                if user.get('data_ultima_atividade'):
                    st.text(f"Última atividade: {user['data_ultima_atividade']}")
            
            with col_actions:
                st.markdown("**Ações:**")
                
                # Alterar cargo
                novo_cargo = st.selectbox(
                    "Alterar Cargo",
                    ["admin", "desenvolvedor", "gestor", "analista", "visualizador"],
                    index=["admin", "desenvolvedor", "gestor", "analista", "visualizador"].index(user.get('cargo', 'visualizador')),
                    key=f"cargo_{user['id']}"
                )
                
                if st.button("Salvar Cargo", key=f"salvar_cargo_{user['id']}", width="stretch"):
                    if alterar_cargo_usuario(user['id'], novo_cargo):
                        st.success(f"Cargo alterado para {novo_cargo}")
                        st.rerun()
                    else:
                        st.error("Erro ao alterar cargo")
                
                st.divider()
                
                # Ativar/Desativar
                if user.get('ativo'):
                    if st.button("Desativar", key=f"desativar_{user['id']}", width="stretch"):
                        if alterar_status_usuario(user['id'], 0):
                            st.success("Usuário desativado")
                            st.rerun()
                        else:
                            st.error("Erro ao desativar")
                else:
                    if st.button("Ativar", key=f"ativar_{user['id']}", type="primary", width="stretch"):
                        if alterar_status_usuario(user['id'], 1):
                            st.success("Usuário ativado")
                            st.rerun()
                        else:
                            st.error("Erro ao ativar")
                
                st.divider()
                
                # Excluir usuário
                if user.get('username') != 'admin':  # Proteger conta admin
                    if st.button("Excluir", key=f"excluir_{user['id']}", width="stretch"):
                        st.session_state[f'confirmar_exclusao_{user["id"]}'] = True
                    
                    if st.session_state.get(f'confirmar_exclusao_{user["id"]}', False):
                        st.warning("Tem certeza?")
                        col_sim, col_nao = st.columns(2)
                        
                        with col_sim:
                            if st.button("Sim", key=f"confirmar_sim_{user['id']}", type="primary"):
                                if excluir_usuario(user['id']):
                                    st.success("Usuário excluído")
                                    st.session_state[f'confirmar_exclusao_{user["id"]}'] = False
                                    st.rerun()
                                else:
                                    st.error("Erro ao excluir")
                        
                        with col_nao:
                            if st.button("Não", key=f"confirmar_nao_{user['id']}"):
                                st.session_state[f'confirmar_exclusao_{user["id"]}'] = False
                                st.rerun()


def listar_usuarios() -> list:
    """Lista todos os usuários do sistema"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        
        cursor.execute("""
            SELECT id, username, email, nome_completo, cargo, ativo, 
                   data_criacao, data_ultima_atividade
            FROM usuarios
            ORDER BY nome_completo
        """)
        
        usuarios = [dict(row) for row in cursor.fetchall()]
        conexao.close()
        return usuarios
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
        return []


def alterar_cargo_usuario(user_id: int, novo_cargo: str) -> bool:
    """Altera o cargo de um usuário"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("UPDATE usuarios SET cargo = ? WHERE id = ?", (novo_cargo, user_id))
        conexao.commit()
        conexao.close()
        return True
    except:
        return False


def alterar_status_usuario(user_id: int, status: int) -> bool:
    """Ativa ou desativa um usuário"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("UPDATE usuarios SET ativo = ? WHERE id = ?", (status, user_id))
        conexao.commit()
        conexao.close()
        return True
    except:
        return False


def excluir_usuario(user_id: int) -> bool:
    """Exclui um usuário do sistema"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
        conexao.commit()
        conexao.close()
        return True
    except:
        return False
