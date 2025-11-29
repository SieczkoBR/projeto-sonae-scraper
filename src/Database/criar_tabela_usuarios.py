import sqlite3
import hashlib
import os
from datetime import datetime

CAMINHO_BANCO = "data/projetos_sonae.db"

def criar_tabelas_autenticacao():
    """
    Cria as tabelas necessárias para o sistema de autenticação:
    - usuarios: Dados dos usuários aprovados
    - solicitacoes_conta: Solicitações pendentes de aprovação
    - permissoes: Lista de todas as permissões disponíveis
    - cargos: Cargos com suas permissões associadas
    """
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                nome_completo TEXT NOT NULL,
                cargo TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                data_criacao TEXT NOT NULL,
                data_ultima_atividade TEXT,
                criado_por INTEGER,
                FOREIGN KEY (criado_por) REFERENCES usuarios(id)
            )
        """)
        print("✅ Tabela 'usuarios' criada com sucesso!")
        
        # Tabela de solicitações de conta (pendentes de aprovação)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitacoes_conta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                senha_hash TEXT NOT NULL,
                nome_completo TEXT NOT NULL,
                cargo_solicitado TEXT NOT NULL,
                mensagem_solicitacao TEXT,
                status TEXT DEFAULT 'pendente',
                data_solicitacao TEXT NOT NULL,
                data_resposta TEXT,
                respondido_por INTEGER,
                cargo_aprovado TEXT,
                mensagem_resposta TEXT,
                FOREIGN KEY (respondido_por) REFERENCES usuarios(id)
            )
        """)
        print("✅ Tabela 'solicitacoes_conta' criada com sucesso!")
        
        # Tabela de permissões disponíveis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria TEXT
            )
        """)
        print("✅ Tabela 'permissoes' criada com sucesso!")
        
        # Tabela de cargos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cargos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                descricao TEXT,
                nivel_hierarquia INTEGER DEFAULT 0
            )
        """)
        print("✅ Tabela 'cargos' criada com sucesso!")
        
        # Tabela de relacionamento: cargos x permissões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cargo_permissoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cargo_codigo TEXT NOT NULL,
                permissao_codigo TEXT NOT NULL,
                FOREIGN KEY (cargo_codigo) REFERENCES cargos(codigo),
                FOREIGN KEY (permissao_codigo) REFERENCES permissoes(codigo),
                UNIQUE(cargo_codigo, permissao_codigo)
            )
        """)
        print("✅ Tabela 'cargo_permissoes' criada com sucesso!")
        
        # Tabela de relacionamento: usuários x permissões extras
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario_permissoes_extras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                permissao_codigo TEXT NOT NULL,
                concedida_por INTEGER,
                data_concessao TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (permissao_codigo) REFERENCES permissoes(codigo),
                FOREIGN KEY (concedida_por) REFERENCES usuarios(id),
                UNIQUE(usuario_id, permissao_codigo)
            )
        """)
        print("✅ Tabela 'usuario_permissoes_extras' criada com sucesso!")
        
        # Criar índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_solicitacoes_status ON solicitacoes_conta(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_cargo ON usuarios(cargo)")
        
        print("✅ Índices criados com sucesso!")
        
        # Inserir permissões padrão
        permissoes_padrao = [
            # Visualização
            ('view_dashboard', 'Visualizar Dashboard', 'Acesso ao dashboard principal', 'Visualização'),
            ('view_projects', 'Visualizar Projetos', 'Visualizar lista e detalhes de projetos', 'Visualização'),
            ('view_reports', 'Visualizar Relatórios', 'Acessar relatórios salvos', 'Visualização'),
            ('view_ai_insights', 'Visualizar Insights IA', 'Acessar análises de IA', 'Visualização'),
            
            # Criação/Edição
            ('create_reports', 'Criar Relatórios', 'Gerar novos relatórios executivos', 'Criação'),
            ('edit_projects', 'Editar Projetos', 'Modificar informações de projetos', 'Edição'),
            ('delete_reports', 'Deletar Relatórios', 'Remover relatórios salvos', 'Exclusão'),
            ('delete_projects', 'Deletar Projetos', 'Remover projetos do sistema', 'Exclusão'),
            
            # Upload de dados
            ('upload_files', 'Upload de Arquivos', 'Fazer upload de documentos', 'Upload'),
            ('import_data', 'Importar Dados', 'Importar dados via Excel/PDF/Word', 'Upload'),
            
            # Administração
            ('manage_users', 'Gerenciar Usuários', 'Criar, editar e desativar usuários', 'Administração'),
            ('approve_accounts', 'Aprovar Contas', 'Aprovar ou negar solicitações de conta', 'Administração'),
            ('manage_permissions', 'Gerenciar Permissões', 'Atribuir permissões especiais', 'Administração'),
            ('view_logs', 'Visualizar Logs', 'Acessar logs do sistema', 'Administração'),
            ('system_config', 'Configurar Sistema', 'Alterar configurações do sistema', 'Administração'),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO permissoes (codigo, nome, descricao, categoria)
            VALUES (?, ?, ?, ?)
        """, permissoes_padrao)
        
        print("✅ Permissões padrão inseridas!")
        
        # Inserir cargos padrão
        cargos_padrao = [
            ('admin', 'Administrador', 'Acesso total ao sistema', 100),
            ('gestor_projetos', 'Gestor de Projetos', 'Gerencia projetos e relatórios', 80),
            ('analista', 'Analista', 'Cria relatórios e analisa dados', 60),
            ('dev', 'Desenvolvedor', 'Acesso técnico e manutenção', 70),
            ('visualizador', 'Visualizador', 'Apenas visualização de dados', 20),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO cargos (codigo, nome, descricao, nivel_hierarquia)
            VALUES (?, ?, ?, ?)
        """, cargos_padrao)
        
        print("✅ Cargos padrão inseridos!")
        
        # Associar permissões aos cargos
        cargo_permissoes_padrao = [
            # Admin - todas as permissões
            ('admin', 'view_dashboard'),
            ('admin', 'view_projects'),
            ('admin', 'view_reports'),
            ('admin', 'view_ai_insights'),
            ('admin', 'create_reports'),
            ('admin', 'edit_projects'),
            ('admin', 'delete_reports'),
            ('admin', 'delete_projects'),
            ('admin', 'upload_files'),
            ('admin', 'import_data'),
            ('admin', 'manage_users'),
            ('admin', 'approve_accounts'),
            ('admin', 'manage_permissions'),
            ('admin', 'view_logs'),
            ('admin', 'system_config'),
            
            # Gestor de Projetos
            ('gestor_projetos', 'view_dashboard'),
            ('gestor_projetos', 'view_projects'),
            ('gestor_projetos', 'view_reports'),
            ('gestor_projetos', 'view_ai_insights'),
            ('gestor_projetos', 'create_reports'),
            ('gestor_projetos', 'edit_projects'),
            ('gestor_projetos', 'delete_reports'),
            ('gestor_projetos', 'upload_files'),
            ('gestor_projetos', 'import_data'),
            
            # Analista
            ('analista', 'view_dashboard'),
            ('analista', 'view_projects'),
            ('analista', 'view_reports'),
            ('analista', 'view_ai_insights'),
            ('analista', 'create_reports'),
            ('analista', 'upload_files'),
            
            # Desenvolvedor
            ('dev', 'view_dashboard'),
            ('dev', 'view_projects'),
            ('dev', 'view_reports'),
            ('dev', 'view_ai_insights'),
            ('dev', 'create_reports'),
            ('dev', 'edit_projects'),
            ('dev', 'upload_files'),
            ('dev', 'import_data'),
            ('dev', 'view_logs'),
            
            # Visualizador
            ('visualizador', 'view_dashboard'),
            ('visualizador', 'view_projects'),
            ('visualizador', 'view_reports'),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO cargo_permissoes (cargo_codigo, permissao_codigo)
            VALUES (?, ?)
        """, cargo_permissoes_padrao)
        
        print("✅ Permissões associadas aos cargos!")
        
        conexao.commit()
        print("\n🎉 Banco de dados preparado para sistema de autenticação!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()


def criar_usuario_admin(username="admin", senha="admin123", email="admin@mcsonae.com", nome_completo="Administrador do Sistema"):
    """
    Cria o usuário administrador inicial.
    """
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        # Verificar se já existe admin
        cursor.execute("SELECT id FROM usuarios WHERE cargo = 'admin'")
        if cursor.fetchone():
            print("⚠️ Já existe um usuário administrador no sistema!")
            return
        
        # Hash da senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        # Data atual
        data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Inserir admin
        cursor.execute("""
            INSERT INTO usuarios (username, email, senha_hash, nome_completo, cargo, ativo, data_criacao)
            VALUES (?, ?, ?, ?, 'admin', 1, ?)
        """, (username, email, senha_hash, nome_completo, data_criacao))
        
        conexao.commit()
        
        print(f"\n✅ Usuário administrador criado com sucesso!")
        print(f"   Username: {username}")
        print(f"   Senha: {senha}")
        print(f"   Email: {email}")
        print(f"\n⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()


if __name__ == "__main__":
    print("=" * 60)
    print("CRIANDO ESTRUTURA DE AUTENTICAÇÃO")
    print("=" * 60)
    
    criar_tabelas_autenticacao()
    
    print("\n" + "=" * 60)
    print("CRIANDO USUÁRIO ADMINISTRADOR")
    print("=" * 60)
    
    criar_usuario_admin()
