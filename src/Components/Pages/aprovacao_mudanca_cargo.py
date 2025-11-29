import streamlit as st
from Auth.autenticacao import AuthManager
import sqlite3
import os

def render_aprovacao_mudanca_cargo_page():
    """Página para aprovar/negar solicitações de mudança de cargo"""
    st.title("Aprovar Mudança de Cargo")
    
    cargo = st.session_state.get('cargo', '')
    
    if cargo != 'admin':
        st.error("Acesso negado! Apenas administradores podem acessar esta página.")
        return
    
    solicitacoes = listar_mudancas_pendentes()
    
    if not solicitacoes:
        st.success("Não há solicitações de mudança de cargo pendentes! 🎉")
        return
    
    st.info(f"Você tem **{len(solicitacoes)}** solicitações pendentes")
    
    for sol in solicitacoes:
        with st.expander(f"🔄 {sol['nome_completo']} (@{sol['username']}) - {sol['cargo_atual']} → {sol['cargo_solicitado']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Informações:**")
                st.text(f"Cargo Atual: {sol['cargo_atual'].upper()}")
                st.text(f"Cargo Solicitado: {sol['cargo_solicitado'].upper()}")
                st.text(f"Data da Solicitação: {sol['data_solicitacao']}")
                
                if sol.get('justificativa'):
                    st.markdown("**Justificativa:**")
                    st.write(sol['justificativa'])
            
            with col2:
                st.markdown("**Ações:**")
                
                # Aprovar
                if st.button(f"✅ Aprovar", key=f"aprovar_{sol['id']}", type="primary", width="stretch"):
                    if aprovar_mudanca_cargo(sol['usuario_id'], sol['cargo_solicitado'], sol['id']):
                        st.success(f"Cargo de {sol['nome_completo']} alterado para {sol['cargo_solicitado']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Erro ao aprovar mudança")
                
                # Negar
                with st.form(f"form_negar_{sol['id']}"):
                    motivo = st.text_area(
                        "Motivo da Negação",
                        placeholder="Explique por que a solicitação foi negada...",
                        key=f"motivo_{sol['id']}"
                    )
                    
                    if st.form_submit_button("❌ Negar", width="stretch"):
                        if negar_mudanca_cargo(sol['id'], motivo):
                            st.success("Solicitação negada")
                            st.rerun()
                        else:
                            st.error("Erro ao negar solicitação")


def listar_mudancas_pendentes() -> list:
    """Lista todas as solicitações de mudança de cargo pendentes"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        
        cursor.execute("""
            SELECT 
                mc.id,
                mc.usuario_id,
                mc.cargo_solicitado,
                mc.justificativa,
                mc.data_solicitacao,
                u.nome_completo,
                u.username,
                u.cargo as cargo_atual
            FROM mudancas_cargo mc
            JOIN usuarios u ON mc.usuario_id = u.id
            WHERE mc.status = 'pendente'
            ORDER BY mc.data_solicitacao DESC
        """)
        
        solicitacoes = [dict(row) for row in cursor.fetchall()]
        conexao.close()
        return solicitacoes
    except:
        return []


def aprovar_mudanca_cargo(usuario_id: int, novo_cargo: str, solicitacao_id: int) -> bool:
    """Aprova mudança de cargo"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        # Atualizar cargo do usuário
        cursor.execute("UPDATE usuarios SET cargo = ? WHERE id = ?", (novo_cargo, usuario_id))
        
        # Marcar solicitação como aprovada
        cursor.execute("""
            UPDATE mudancas_cargo 
            SET status = 'aprovado', 
                data_resposta = datetime('now'),
                respondido_por = ?
            WHERE id = ?
        """, (st.session_state.get('user_id'), solicitacao_id))
        
        conexao.commit()
        conexao.close()
        return True
    except:
        return False


def negar_mudanca_cargo(solicitacao_id: int, motivo: str = None) -> bool:
    """Nega mudança de cargo"""
    CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        cursor.execute("""
            UPDATE mudancas_cargo 
            SET status = 'negado', 
                data_resposta = datetime('now'),
                respondido_por = ?,
                motivo_negacao = ?
            WHERE id = ?
        """, (st.session_state.get('user_id'), motivo, solicitacao_id))
        
        conexao.commit()
        conexao.close()
        return True
    except:
        return False
