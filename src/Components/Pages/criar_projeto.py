import streamlit as st
import sqlite3
import os
import sys
from datetime import datetime

# Adicionar path correto
caminho_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, caminho_src)

from Readers.criptograph import encriptar_dado

def render_criar_projeto_page():
    """Página para criar novos projetos"""
    st.title("Criar Novo Projeto")
    
    # Tabs para diferentes métodos de criação
    tab1, tab2 = st.tabs(["Formulário Manual", "Upload de Arquivo"])
    
    with tab1:
        render_criar_projeto_manual()
    
    with tab2:
        render_criar_projeto_upload()


def render_criar_projeto_manual():
    """Formulário manual para criar projeto"""
    st.markdown("### Criar Projeto Manualmente")
    
    with st.form("form_criar_projeto"):
        st.subheader("Informações Básicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Projeto *", help="Nome identificador do projeto")
            data_inicio = st.date_input("Data de Início *", help="Data de início do projeto")
            status = st.selectbox("Status *", ["Planejado", "Em Andamento", "Concluído", "Cancelado"])
        
        with col2:
            responsavel = st.text_input("Responsável *", help="Nome do responsável (será criptografado)")
            data_fim = st.date_input("Data de Término Prevista", help="Data prevista (opcional)")
            prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Crítica"])
        
        st.divider()
        st.subheader("Informações Financeiras")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            orcamento = st.number_input("Orçamento Total (€)", min_value=0.0, step=1000.0)
        
        with col4:
            custo_atual = st.number_input("Custo Atual (€)", min_value=0.0, step=100.0)
        
        with col5:
            progresso = st.slider("Progresso (%)", 0, 100, 0)
        
        st.divider()
        st.subheader("Detalhes Adicionais")
        
        descricao = st.text_area("Descrição", placeholder="Descreva o projeto...", height=150)
        categoria = st.text_input("Categoria/Departamento", placeholder="Ex: TI, Marketing...")
        tags = st.text_input("Tags", placeholder="Ex: digital, transformação (separadas por vírgula)")
        
        st.divider()
        
        col_submit, col_cancel = st.columns([3, 1])
        
        with col_submit:
            submit = st.form_submit_button("Criar Projeto", type="primary", width="stretch")
        
        with col_cancel:
            cancel = st.form_submit_button("Cancelar", width="stretch")
    
    if cancel:
        st.info("Operação cancelada")
        st.rerun()
    
    if submit:
        # Validações
        if not nome or not responsavel or not data_inicio or not status:
            st.error("Preencha todos os campos obrigatórios (*)")
        else:
            # Verificar duplicata
            if verificar_projeto_existente(nome):
                st.error(f"Já existe um projeto com o nome '{nome}'")
            else:
                # Criar projeto
                sucesso, mensagem = criar_projeto_db(
                    nome=nome,
                    responsavel=responsavel,
                    data_inicio=data_inicio.strftime("%Y-%m-%d"),
                    data_fim=data_fim.strftime("%Y-%m-%d") if data_fim else None,
                    status=status,
                    prioridade=prioridade,
                    orcamento=orcamento,
                    custo_atual=custo_atual,
                    progresso=progresso,
                    descricao=descricao,
                    categoria=categoria,
                    tags=tags,
                    criado_por=st.session_state.get('user_id')
                )
                
                if sucesso:
                    st.success(mensagem)
                    st.balloons()
                    st.info("Redirecionando...")
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(mensagem)


def render_criar_projeto_upload():
    """Upload de arquivo para criar projeto"""
    st.markdown("### Criar Projeto via Upload")
    st.info("Upload de PDF/Word/Excel com extração por IA - Em implementação")
    
    nome = st.text_input("Nome do Projeto *", key="upload_nome")
    arquivo = st.file_uploader("Upload arquivo", type=['pdf', 'docx', 'xlsx'], key="upload_file")
    
    if st.button("Processar", type="primary"):
        if not nome:
            st.error("Nome do projeto é obrigatório")
        elif not arquivo:
            st.error("Selecione um arquivo")
        else:
            st.info("Funcionalidade de IA em desenvolvimento. Use o formulário manual por enquanto.")


def verificar_projeto_existente(nome: str) -> bool:
    """Verifica se já existe projeto com o nome"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM projetos WHERE LOWER(nome) = LOWER(?)", (nome,))
        count = cursor.fetchone()[0]
        conexao.close()
        return count > 0
    except:
        return False


def criar_projeto_db(
    nome: str,
    responsavel: str,
    data_inicio: str,
    status: str,
    criado_por: int,
    data_fim: str = None,
    prioridade: str = "Média",
    orcamento: float = 0.0,
    custo_atual: float = 0.0,
    progresso: int = 0,
    descricao: str = None,
    categoria: str = None,
    tags: str = None
) -> tuple[bool, str]:
    """Cria projeto no banco"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    conexao = None
    
    try:
        # Criptografar responsável
        responsavel_cript = encriptar_dado(responsavel)
        
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        cursor.execute("""
            INSERT INTO projetos (
                nome, nome_projeto, responsavel, data_inicio, data_fim,
                status, prioridade, orcamento, custo_atual, progresso,
                descricao, categoria, tags, criado_por, criado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nome, nome, responsavel_cript, data_inicio, data_fim,
            status, prioridade, orcamento, custo_atual, progresso,
            descricao, categoria, tags, criado_por, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        conexao.commit()
        conexao.close()
        
        return True, f"Projeto '{nome}' criado com sucesso!"
        
    except Exception as e:
        if conexao:
            conexao.rollback()
            conexao.close()
        return False, f"Erro ao criar projeto: {str(e)}"
