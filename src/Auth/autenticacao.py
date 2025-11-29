import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, Dict, List

CAMINHO_BANCO = "data/projetos_sonae.db"

class AuthManager:
    """Gerenciador de autenticação e autorização"""
    
    def __init__(self):
        self.caminho_banco = CAMINHO_BANCO
    
    @staticmethod
    def hash_senha(senha: str) -> str:
        """Gera hash SHA-256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def verificar_login(self, username: str, senha: str) -> Optional[Dict]:
        """
        Verifica credenciais de login.
        
        Returns:
            Dict com dados do usuário se válido, None caso contrário
        """
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            senha_hash = self.hash_senha(senha)
            
            cursor.execute("""
                SELECT id, username, email, nome_completo, cargo, ativo
                FROM usuarios
                WHERE username = ? AND senha_hash = ?
            """, (username, senha_hash))
            
            row = cursor.fetchone()
            
            if row and row['ativo'] == 1:
                # Atualizar última atividade
                cursor.execute("""
                    UPDATE usuarios
                    SET data_ultima_atividade = ?
                    WHERE id = ?
                """, (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), row['id']))
                
                conexao.commit()
                
                return {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'nome_completo': row['nome_completo'],
                    'cargo': row['cargo']
                }
            
            return None
            
        except Exception as e:
            print(f"Erro ao verificar login: {e}")
            return None
        finally:
            if conexao:
                conexao.close()
    
    def criar_solicitacao_conta(
        self,
        username: str,
        email: str,
        senha: str,
        nome_completo: str,
        cargo_solicitado: str,
        mensagem_solicitacao: str = None
    ) -> bool:
        """Cria uma nova solicitação de conta"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            # Verificar se username ou email já existem
            cursor.execute("""
                SELECT id FROM usuarios WHERE username = ? OR email = ?
            """, (username, email))
            
            if cursor.fetchone():
                print("Username ou email já cadastrado")
                return False
            
            # Verificar se já tem solicitação pendente
            cursor.execute("""
                SELECT id FROM solicitacoes_conta 
                WHERE (username = ? OR email = ?) AND status = 'pendente'
            """, (username, email))
            
            if cursor.fetchone():
                print("Já existe uma solicitação pendente para este username/email")
                return False
            
            senha_hash = self.hash_senha(senha)
            data_solicitacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO solicitacoes_conta 
                (username, email, senha_hash, nome_completo, cargo_solicitado, 
                 mensagem_solicitacao, data_solicitacao, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pendente')
            """, (username, email, senha_hash, nome_completo, cargo_solicitado,
                  mensagem_solicitacao, data_solicitacao))
            
            conexao.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao criar solicitação: {e}")
            if conexao:
                conexao.rollback()
            return False
        finally:
            if conexao:
                conexao.close()
    
    def listar_solicitacoes_pendentes(self) -> List[Dict]:
        """Lista todas as solicitações pendentes"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT * FROM solicitacoes_conta
                WHERE status = 'pendente'
                ORDER BY data_solicitacao DESC
            """)
            
            rows = cursor.fetchall()
            solicitacoes = []
            
            for row in rows:
                solicitacoes.append({
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'nome_completo': row['nome_completo'],
                    'cargo_solicitado': row['cargo_solicitado'],
                    'mensagem_solicitacao': row['mensagem_solicitacao'],
                    'data_solicitacao': row['data_solicitacao']
                })
            
            return solicitacoes
            
        except Exception as e:
            print(f"Erro ao listar solicitações: {e}")
            return []
        finally:
            if conexao:
                conexao.close()
    
    def contar_solicitacoes_pendentes(self) -> int:
        """Conta quantas solicitações estão pendentes"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM solicitacoes_conta WHERE status = 'pendente'
            """)
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            print(f"Erro ao contar solicitações: {e}")
            return 0
        finally:
            if conexao:
                conexao.close()
    
    def aprovar_solicitacao(
        self,
        solicitacao_id: int,
        admin_id: int,
        cargo_aprovado: str = None,
        mensagem_resposta: str = None
    ) -> bool:
        """Aprova uma solicitação de conta e cria o usuário"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            # Buscar solicitação
            cursor.execute("""
                SELECT * FROM solicitacoes_conta WHERE id = ?
            """, (solicitacao_id,))
            
            solicitacao = cursor.fetchone()
            if not solicitacao or solicitacao['status'] != 'pendente':
                return False
            
            # Cargo final (aprovado ou solicitado)
            cargo_final = cargo_aprovado if cargo_aprovado else solicitacao['cargo_solicitado']
            
            # Criar usuário
            data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO usuarios 
                (username, email, senha_hash, nome_completo, cargo, ativo, data_criacao, criado_por)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                solicitacao['username'],
                solicitacao['email'],
                solicitacao['senha_hash'],
                solicitacao['nome_completo'],
                cargo_final,
                data_criacao,
                admin_id
            ))
            
            # Atualizar solicitação
            cursor.execute("""
                UPDATE solicitacoes_conta
                SET status = 'aprovada',
                    data_resposta = ?,
                    respondido_por = ?,
                    cargo_aprovado = ?,
                    mensagem_resposta = ?
                WHERE id = ?
            """, (datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                  admin_id,
                  cargo_final,
                  mensagem_resposta,
                  solicitacao_id))
            
            conexao.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao aprovar solicitação: {e}")
            if conexao:
                conexao.rollback()
            return False
        finally:
            if conexao:
                conexao.close()
    
    def negar_solicitacao(
        self,
        solicitacao_id: int,
        admin_id: int,
        mensagem_resposta: str = None
    ) -> bool:
        """Nega uma solicitação de conta"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            cursor.execute("""
                UPDATE solicitacoes_conta
                SET status = 'negada',
                    data_resposta = ?,
                    respondido_por = ?,
                    mensagem_resposta = ?
                WHERE id = ? AND status = 'pendente'
            """, (datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                  admin_id,
                  mensagem_resposta,
                  solicitacao_id))
            
            conexao.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erro ao negar solicitação: {e}")
            if conexao:
                conexao.rollback()
            return False
        finally:
            if conexao:
                conexao.close()
    
    def obter_permissoes_usuario(self, user_id: int) -> List[str]:
        """Obtém todas as permissões de um usuário (cargo + extras)"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            # Buscar cargo do usuário
            cursor.execute("SELECT cargo FROM usuarios WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return []
            
            cargo = row[0]
            
            # Buscar permissões do cargo
            cursor.execute("""
                SELECT p.codigo
                FROM permissoes p
                JOIN cargo_permissoes cp ON p.codigo = cp.permissao_codigo
                WHERE cp.cargo_codigo = ?
            """, (cargo,))
            
            permissoes_cargo = [row[0] for row in cursor.fetchall()]
            
            # Buscar permissões extras do usuário
            cursor.execute("""
                SELECT permissao_codigo
                FROM usuario_permissoes_extras
                WHERE usuario_id = ?
            """, (user_id,))
            
            permissoes_extras = [row[0] for row in cursor.fetchall()]
            
            # Combinar e remover duplicatas
            todas_permissoes = list(set(permissoes_cargo + permissoes_extras))
            
            return todas_permissoes
            
        except Exception as e:
            print(f"Erro ao obter permissões: {e}")
            return []
        finally:
            if conexao:
                conexao.close()
    
    def verificar_permissao(self, user_id: int, permissao: str) -> bool:
        """Verifica se usuário tem determinada permissão"""
        permissoes = self.obter_permissoes_usuario(user_id)
        return permissao in permissoes
    
    def listar_cargos_disponiveis(self) -> List[Dict]:
        """Lista todos os cargos disponíveis para seleção"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT codigo, nome, descricao, nivel_hierarquia
                FROM cargos
                WHERE codigo != 'admin'
                ORDER BY nivel_hierarquia DESC
            """)
            
            cargos = []
            for row in cursor.fetchall():
                cargos.append({
                    'codigo': row['codigo'],
                    'nome': row['nome'],
                    'descricao': row['descricao'],
                    'nivel_hierarquia': row['nivel_hierarquia']
                })
            
            return cargos
            
        except Exception as e:
            print(f"Erro ao listar cargos: {e}")
            return []
        finally:
            if conexao:
                conexao.close()
    
    def alterar_senha(self, user_id: int, senha_atual: str, senha_nova: str) -> tuple[bool, str]:
        """
        Altera a senha do usuário.
        Returns: (sucesso, mensagem)
        """
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            # Verificar senha atual
            senha_atual_hash = self.hash_senha(senha_atual)
            cursor.execute("""
                SELECT id FROM usuarios WHERE id = ? AND senha_hash = ?
            """, (user_id, senha_atual_hash))
            
            if not cursor.fetchone():
                return False, "Senha atual incorreta"
            
            # Atualizar senha
            senha_nova_hash = self.hash_senha(senha_nova)
            cursor.execute("""
                UPDATE usuarios SET senha_hash = ? WHERE id = ?
            """, (senha_nova_hash, user_id))
            
            conexao.commit()
            return True, "Senha alterada com sucesso"
            
        except Exception as e:
            print(f"Erro ao alterar senha: {e}")
            if conexao:
                conexao.rollback()
            return False, f"Erro: {e}"
        finally:
            if conexao:
                conexao.close()
    
    def solicitar_mudanca_cargo(
        self,
        user_id: int,
        cargo_solicitado: str,
        mensagem: str = None
    ) -> bool:
        """Cria solicitação de mudança de cargo"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            # Buscar cargo atual
            cursor.execute("SELECT cargo FROM usuarios WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            cargo_atual = row[0]
            
            # Verificar se já tem solicitação pendente
            cursor.execute("""
                SELECT id FROM solicitacoes_mudanca_cargo
                WHERE usuario_id = ? AND status = 'pendente'
            """, (user_id,))
            
            if cursor.fetchone():
                print("Já existe uma solicitação pendente")
                return False
            
            # Criar solicitação
            cursor.execute("""
                INSERT INTO solicitacoes_mudanca_cargo
                (usuario_id, cargo_atual, cargo_solicitado, mensagem_solicitacao,
                 data_solicitacao, status)
                VALUES (?, ?, ?, ?, ?, 'pendente')
            """, (user_id, cargo_atual, cargo_solicitado, mensagem,
                  datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            
            conexao.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao solicitar mudança de cargo: {e}")
            if conexao:
                conexao.rollback()
            return False
        finally:
            if conexao:
                conexao.close()
    
    def excluir_conta(self, user_id: int, username: str, senha: str) -> tuple[bool, str]:
        """
        Exclui conta do usuário após validação.
        Remove COMPLETAMENTE nome, email e senha.
        Returns: (sucesso, mensagem)
        """
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            # Verificar credenciais
            senha_hash = self.hash_senha(senha)
            cursor.execute("""
                SELECT id FROM usuarios 
                WHERE id = ? AND username = ? AND senha_hash = ?
            """, (user_id, username, senha_hash))
            
            if not cursor.fetchone():
                return False, "Credenciais inválidas"
            
            # Não permitir exclusão de admin
            cursor.execute("SELECT cargo FROM usuarios WHERE id = ?", (user_id,))
            cargo = cursor.fetchone()[0]
            if cargo == 'admin':
                return False, "Conta de administrador não pode ser excluída"
            
            # Excluir COMPLETAMENTE
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
            cursor.execute("DELETE FROM usuario_permissoes_extras WHERE usuario_id = ?", (user_id,))
            cursor.execute("DELETE FROM solicitacoes_mudanca_cargo WHERE usuario_id = ?", (user_id,))
            
            # Atualizar relatórios (manter, mas sem user_id)
            cursor.execute("UPDATE relatorios_salvos SET user_id = NULL WHERE user_id = ?", (user_id,))
            
            conexao.commit()
            return True, "Conta excluída com sucesso"
            
        except Exception as e:
            print(f"Erro ao excluir conta: {e}")
            if conexao:
                conexao.rollback()
            return False, f"Erro: {e}"
        finally:
            if conexao:
                conexao.close()
    
    def listar_todos_usuarios(self, filtro_cargo: str = None, busca: str = None) -> List[Dict]:
        """Lista todos os usuários com filtros opcionais"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            query = "SELECT * FROM usuarios WHERE 1=1"
            params = []
            
            if filtro_cargo:
                query += " AND cargo = ?"
                params.append(filtro_cargo)
            
            if busca:
                query += " AND (username LIKE ? OR nome_completo LIKE ? OR email LIKE ?)"
                busca_param = f"%{busca}%"
                params.extend([busca_param, busca_param, busca_param])
            
            query += " ORDER BY nome_completo"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            usuarios = []
            for row in rows:
                usuarios.append({
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'nome_completo': row['nome_completo'],
                    'cargo': row['cargo'],
                    'ativo': row['ativo'],
                    'data_criacao': row['data_criacao'],
                    'data_ultima_atividade': row['data_ultima_atividade']
                })
            
            return usuarios
            
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
        finally:
            if conexao:
                conexao.close()
    
    def listar_solicitacoes_mudanca_cargo(self) -> List[Dict]:
        """Lista solicitações de mudança de cargo pendentes"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT smc.*, u.username, u.nome_completo, u.email
                FROM solicitacoes_mudanca_cargo smc
                JOIN usuarios u ON smc.usuario_id = u.id
                WHERE smc.status = 'pendente'
                ORDER BY smc.data_solicitacao DESC
            """)
            
            rows = cursor.fetchall()
            solicitacoes = []
            
            for row in rows:
                solicitacoes.append({
                    'id': row['id'],
                    'usuario_id': row['usuario_id'],
                    'username': row['username'],
                    'nome_completo': row['nome_completo'],
                    'email': row['email'],
                    'cargo_atual': row['cargo_atual'],
                    'cargo_solicitado': row['cargo_solicitado'],
                    'mensagem_solicitacao': row['mensagem_solicitacao'],
                    'data_solicitacao': row['data_solicitacao']
                })
            
            return solicitacoes
            
        except Exception as e:
            print(f"Erro ao listar solicitações: {e}")
            return []
        finally:
            if conexao:
                conexao.close()
    
    def aprovar_mudanca_cargo(
        self,
        solicitacao_id: int,
        admin_id: int,
        mensagem_resposta: str = None
    ) -> bool:
        """Aprova mudança de cargo"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            # Buscar solicitação
            cursor.execute("""
                SELECT * FROM solicitacoes_mudanca_cargo WHERE id = ?
            """, (solicitacao_id,))
            
            sol = cursor.fetchone()
            if not sol or sol['status'] != 'pendente':
                return False
            
            # Atualizar cargo do usuário
            cursor.execute("""
                UPDATE usuarios SET cargo = ? WHERE id = ?
            """, (sol['cargo_solicitado'], sol['usuario_id']))
            
            # Atualizar solicitação
            cursor.execute("""
                UPDATE solicitacoes_mudanca_cargo
                SET status = 'aprovada',
                    data_resposta = ?,
                    respondido_por = ?,
                    mensagem_resposta = ?
                WHERE id = ?
            """, (datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                  admin_id, mensagem_resposta, solicitacao_id))
            
            conexao.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao aprovar mudança: {e}")
            if conexao:
                conexao.rollback()
            return False
        finally:
            if conexao:
                conexao.close()
    
    def negar_mudanca_cargo(
        self,
        solicitacao_id: int,
        admin_id: int,
        mensagem_resposta: str = None
    ) -> bool:
        """Nega mudança de cargo"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            cursor.execute("""
                UPDATE solicitacoes_mudanca_cargo
                SET status = 'negada',
                    data_resposta = ?,
                    respondido_por = ?,
                    mensagem_resposta = ?
                WHERE id = ? AND status = 'pendente'
            """, (datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                  admin_id, mensagem_resposta, solicitacao_id))
            
            conexao.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erro ao negar mudança: {e}")
            if conexao:
                conexao.rollback()
            return False
        finally:
            if conexao:
                conexao.close()
    
    def contar_solicitacoes_mudanca_cargo(self) -> int:
        """Conta solicitações de mudança de cargo pendentes"""
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM solicitacoes_mudanca_cargo WHERE status = 'pendente'
            """)
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            print(f"Erro ao contar: {e}")
            return 0
        finally:
            if conexao:
                conexao.close()
