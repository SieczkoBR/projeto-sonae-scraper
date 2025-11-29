import streamlit as st
import sqlite3
import os
import sys
import hashlib
from datetime import datetime

# Adicionar path correto
caminho_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, caminho_src)

from Readers.criptograph import encriptar_dado, decriptar_dado

def render_gerenciar_projetos_page():
    """Página para gestores gerenciarem seus projetos"""
    st.title("Gerenciar Meus Projetos")
    
    cargo = st.session_state.get('cargo', '')
    
    if cargo not in ['gestor', 'desenvolvedor', 'admin']:
        st.error("Acesso negado! Apenas gestores, desenvolvedores e administradores podem gerenciar projetos.")
        return
    
    # Buscar projetos do usuário
    user_id = st.session_state.get('user_id')
    projetos = buscar_projetos_do_usuario(user_id)
    
    if not projetos:
        st.info("Você ainda não criou nenhum projeto.")
        return
    
    # Seletor de projeto
    st.subheader("Selecione um Projeto")
    
    opcoes = {f"{p['nome']} (ID: {p['id']})": p['id'] for p in projetos}
    projeto_selecionado = st.selectbox("Escolha um projeto", list(opcoes.keys()))
    
    if projeto_selecionado:
        projeto_id = opcoes[projeto_selecionado]
        projeto = buscar_projeto_completo(projeto_id)
        
        if projeto:
            st.divider()
            tab1, tab2 = st.tabs(["Editar Projeto", "Excluir Projeto"])
            
            with tab1:
                render_editar_projeto(projeto)
            
            with tab2:
                render_excluir_projeto(projeto)


def buscar_projetos_do_usuario(user_id: int) -> list:
    """Busca projetos criados pelo usuário"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, status FROM projetos WHERE criado_por = ? ORDER BY criado_em DESC", (user_id,))
        projetos = [dict(row) for row in cursor.fetchall()]
        conexao.close()
        return projetos
    except:
        return []


def buscar_projeto_completo(projeto_id: int) -> dict:
    """Busca detalhes completos do projeto"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM projetos WHERE id = ?", (projeto_id,))
        row = cursor.fetchone()
        conexao.close()
        
        if row:
            projeto = dict(row)
            if projeto.get('responsavel'):
                try:
                    projeto['responsavel'] = decriptar_dado(projeto['responsavel'])
                except:
                    projeto['responsavel'] = 'Erro ao decriptar'
            return projeto
        return None
    except:
        return None


def render_editar_projeto(projeto: dict):
    """Formulário para editar projeto"""
    st.markdown("### Editar Informações")
    
    with st.form("form_editar"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome *", value=projeto.get('nome', ''))
            data_inicio = st.date_input("Data Início *", value=datetime.strptime(projeto.get('data_inicio', '2025-01-01'), "%Y-%m-%d") if projeto.get('data_inicio') else None)
            status = st.selectbox("Status *", ["Planejado", "Em Andamento", "Concluído", "Cancelado"], index=["Planejado", "Em Andamento", "Concluído", "Cancelado"].index(projeto.get('status', 'Planejado')))
        
        with col2:
            responsavel = st.text_input("Responsável *", value=projeto.get('responsavel', ''))
            data_fim_value = datetime.strptime(projeto.get('data_fim'), "%Y-%m-%d") if projeto.get('data_fim') else None
            data_fim = st.date_input("Data Término", value=data_fim_value)
            prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Crítica"], index=["Baixa", "Média", "Alta", "Crítica"].index(projeto.get('prioridade', 'Média')))
        
        st.divider()
        
        col3, col4, col5 = st.columns(3)
        with col3:
            orcamento = st.number_input("Orçamento (€)", min_value=0.0, value=float(projeto.get('orcamento', 0.0)), step=1000.0)
        with col4:
            custo_atual = st.number_input("Custo Atual (€)", min_value=0.0, value=float(projeto.get('custo_atual', 0.0)), step=100.0)
        with col5:
            progresso = st.slider("Progresso (%)", 0, 100, int(projeto.get('progresso', 0)))
        
        st.divider()
        
        descricao = st.text_area("Descrição", value=projeto.get('descricao', ''), height=150)
        categoria = st.text_input("Categoria", value=projeto.get('categoria', ''))
        tags = st.text_input("Tags", value=projeto.get('tags', ''))
        
        col_s, col_c = st.columns([3, 1])
        with col_s:
            submit = st.form_submit_button("Salvar Alterações", type="primary", width="stretch")
        with col_c:
            cancel = st.form_submit_button("Cancelar", width="stretch")
    
    if cancel:
        st.rerun()
    
    if submit:
        if not nome or not responsavel or not data_inicio or not status:
            st.error("Preencha todos os campos obrigatórios")
        else:
            sucesso, msg = atualizar_projeto_db(
                projeto['id'], nome, responsavel,
                data_inicio.strftime("%Y-%m-%d"),
                data_fim.strftime("%Y-%m-%d") if data_fim else None,
                status, prioridade, orcamento, custo_atual,
                progresso, descricao, categoria, tags
            )
            
            if sucesso:
                st.success(msg)
                st.balloons()
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error(msg)


def render_excluir_projeto(projeto: dict):
    """Interface para excluir projeto"""
    st.markdown("### Excluir Projeto Permanentemente")
    
    st.warning(f"**ATENÇÃO**: Você está prestes a excluir permanentemente o projeto **{projeto.get('nome')}**. Esta ação não pode ser desfeita!")
    
    with st.form("form_excluir"):
        st.subheader("Confirme sua identidade")
        login = st.text_input("Login")
        senha = st.text_input("Senha", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            confirmar = st.form_submit_button("CONFIRMAR EXCLUSÃO", type="primary", width="stretch")
        with col2:
            cancelar = st.form_submit_button("Cancelar", width="stretch")
    
    if cancelar:
        st.rerun()
    
    if confirmar:
        if not login or not senha:
            st.error("Login e senha obrigatórios")
        elif verificar_credenciais(login, senha):
            sucesso, msg = excluir_projeto_db(projeto['id'])
            if sucesso:
                st.success(msg)
                st.balloons()
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error(msg)
        else:
            st.error("Credenciais incorretas")


def atualizar_projeto_db(projeto_id, nome, responsavel, data_inicio, data_fim, status, prioridade, orcamento, custo_atual, progresso, descricao, categoria, tags):
    """Atualiza projeto no banco"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        responsavel_cript = encriptar_dado(responsavel)
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        cursor.execute("""
            UPDATE projetos SET
                nome = ?, nome_projeto = ?, responsavel = ?, data_inicio = ?, data_fim = ?,
                status = ?, prioridade = ?, orcamento = ?, custo_atual = ?, progresso = ?,
                descricao = ?, categoria = ?, tags = ?
            WHERE id = ?
        """, (nome, nome, responsavel_cript, data_inicio, data_fim, status, prioridade,
              orcamento, custo_atual, progresso, descricao, categoria, tags, projeto_id))
        
        conexao.commit()
        conexao.close()
        return True, f"Projeto '{nome}' atualizado!"
    except Exception as e:
        return False, f"Erro: {str(e)}"


def excluir_projeto_db(projeto_id: int):
    """Exclui projeto"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM projetos WHERE id = ?", (projeto_id,))
        nome = cursor.fetchone()[0]
        cursor.execute("DELETE FROM projetos WHERE id = ?", (projeto_id,))
        conexao.commit()
        conexao.close()
        return True, f"Projeto '{nome}' excluído!"
    except Exception as e:
        return False, f"Erro: {str(e)}"


def verificar_credenciais(login: str, senha: str) -> bool:
    """Verifica credenciais do usuário"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE username = ? AND senha_hash = ?", (login, senha_hash))
        resultado = cursor.fetchone()
        conexao.close()
        return resultado is not None
    except:
        return False
