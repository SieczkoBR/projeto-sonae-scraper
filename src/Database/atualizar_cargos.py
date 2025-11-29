import sqlite3
from datetime import datetime

CAMINHO_BANCO = "data/projetos_sonae.db"

def redefinir_cargos_e_permissoes():
    """
    Redefine os cargos e permissões do sistema.
    
    CARGOS DO SISTEMA:
    1. Admin - Acesso total ao sistema (15 permissões) - Nível: 100 (exceção)
    2. Desenvolvedor - Todas funcionalidades exceto admin (11 permissões) - Nível: 73
    3. Gestor - Gerencia projetos, aprova mudanças (11 permissões) - Nível: 73
    4. Analista - Cria relatórios, edita projetos (8 permissões) - Nível: 53
    5. Visualizador - Apenas visualização (4 permissões) - Nível: 27
    
    CÁLCULO DE NÍVEIS HIERÁRQUICOS:
    - Total de permissões: 15
    - Pontos por permissão: 100 ÷ 15 = 6.67
    - Nível = Quantidade de permissões × 6.67 (arredondado)
    - Exceção: Admin sempre = 100
    """
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        print("🔄 Limpando cargos e permissões antigas...")
        
        # Limpar apenas as relações de permissões antigas
        cursor.execute("DELETE FROM cargo_permissoes")
        
        # NÃO deletar cargos - apenas atualizar os existentes e criar os faltantes
        # Isso preserva cargos customizados criados manualmente
        
        # Atualizar/manter cargos com níveis calculados
        cargos_novos = [
            ('admin', 'Administrador', 'Acesso total ao sistema, gerencia usuários e configurações', 100),  # 15 perms - exceção
            ('desenvolvedor', 'Desenvolvedor', 'Acesso completo a funcionalidades do sistema exceto administração de usuários', 73),  # 11 perms
            ('gestor', 'Gestor', 'Gerencia projetos, aprova solicitações, acesso amplo', 73),  # 11 perms
            ('analista', 'Analista', 'Cria e edita relatórios, modifica projetos, visualiza dados', 53),  # 8 perms
            ('visualizador', 'Visualizador', 'Apenas visualização de dashboards e relatórios', 27),  # 4 perms
        ]
        
        print("✅ Atualizando cargos...")
        for cargo in cargos_novos:
            cursor.execute("""
                INSERT OR REPLACE INTO cargos (codigo, nome, descricao, nivel_hierarquia)
                VALUES (?, ?, ?, ?)
            """, cargo)
        
        print("✅ Definindo permissões por cargo...")
        
        # ADMIN - Todas as permissões
        permissoes_admin = [
            'view_dashboard', 'view_projects', 'view_reports', 'view_ai_insights',
            'create_reports', 'edit_projects', 'delete_reports', 'delete_projects',
            'upload_files', 'import_data', 'manage_users', 'approve_accounts',
            'manage_permissions', 'view_logs', 'system_config'
        ]
        
        # DESENVOLVEDOR - Todas funcionalidades exceto admin (11 permissões)
        permissoes_desenvolvedor = [
            'view_dashboard', 'view_projects', 'view_reports', 'view_ai_insights',
            'create_reports', 'edit_projects', 'delete_reports', 'delete_projects',
            'upload_files', 'import_data', 'view_logs'
        ]
        
        # GESTOR - Gerenciamento amplo, sem configurações de sistema (11 permissões)
        permissoes_gestor = [
            'view_dashboard', 'view_projects', 'view_reports', 'view_ai_insights',
            'create_reports', 'edit_projects', 'delete_reports', 'delete_projects',
            'upload_files', 'import_data', 'view_logs'
        ]
        
        # ANALISTA - Criação e edição, sem exclusões (8 permissões)
        permissoes_analista = [
            'view_dashboard', 'view_projects', 'view_reports', 'view_ai_insights',
            'create_reports', 'edit_projects', 'upload_files', 'import_data'
        ]
        
        # VISUALIZADOR - Apenas visualização (4 permissões)
        permissoes_visualizador = [
            'view_dashboard', 'view_projects', 'view_reports', 'view_ai_insights'
        ]
        
        # Inserir permissões
        for perm in permissoes_admin:
            cursor.execute("""
                INSERT OR IGNORE INTO cargo_permissoes (cargo_codigo, permissao_codigo)
                VALUES ('admin', ?)
            """, (perm,))
        
        for perm in permissoes_desenvolvedor:
            cursor.execute("""
                INSERT OR IGNORE INTO cargo_permissoes (cargo_codigo, permissao_codigo)
                VALUES ('desenvolvedor', ?)
            """, (perm,))
        
        for perm in permissoes_gestor:
            cursor.execute("""
                INSERT OR IGNORE INTO cargo_permissoes (cargo_codigo, permissao_codigo)
                VALUES ('gestor', ?)
            """, (perm,))
        
        for perm in permissoes_analista:
            cursor.execute("""
                INSERT OR IGNORE INTO cargo_permissoes (cargo_codigo, permissao_codigo)
                VALUES ('analista', ?)
            """, (perm,))
        
        for perm in permissoes_visualizador:
            cursor.execute("""
                INSERT OR IGNORE INTO cargo_permissoes (cargo_codigo, permissao_codigo)
                VALUES ('visualizador', ?)
            """, (perm,))
        
        conexao.commit()
        
        print("\n✅ Cargos e permissões atualizados com sucesso!")
        print("\n📋 RESUMO DOS CARGOS:")
        print("\n1. 👑 ADMINISTRADOR - Nível 100")
        print("   - Todas as 15 permissões")
        print("   - Gerencia usuários e sistema")
        
        print("\n2. 💻 DESENVOLVEDOR - Nível 73")
        print("   - 11 permissões")
        print("   - Todas funcionalidades exceto administração")
        print("   - Cria, edita e deleta projetos/relatórios")
        
        print("\n3. 👔 GESTOR - Nível 73")
        print("   - 11 permissões")
        print("   - Cria, edita e deleta projetos/relatórios")
        print("   - Não gerencia usuários ou configurações")
        
        print("\n4. 📊 ANALISTA - Nível 53")
        print("   - 8 permissões")
        print("   - Cria relatórios e edita projetos")
        print("   - Não pode deletar")
        
        print("\n5. 👁️ VISUALIZADOR - Nível 27")
        print("   - 4 permissões (apenas visualização)")
        print("   - Acesso read-only")
        
        print("\n" + "="*70)
        print("📊 CÁLCULO: 100 pontos ÷ 15 permissões = 6.67 pontos/permissão")
        print("⚠️  Admin sempre = 100 (exceção à regra)")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()


def criar_tabela_solicitacoes_mudanca_cargo():
    """Cria tabela para solicitações de mudança de cargo"""
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitacoes_mudanca_cargo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                cargo_atual TEXT NOT NULL,
                cargo_solicitado TEXT NOT NULL,
                mensagem_solicitacao TEXT,
                status TEXT DEFAULT 'pendente',
                data_solicitacao TEXT NOT NULL,
                data_resposta TEXT,
                respondido_por INTEGER,
                mensagem_resposta TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (respondido_por) REFERENCES usuarios(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mudanca_cargo_status 
            ON solicitacoes_mudanca_cargo(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mudanca_cargo_usuario 
            ON solicitacoes_mudanca_cargo(usuario_id)
        """)
        
        conexao.commit()
        print("✅ Tabela 'solicitacoes_mudanca_cargo' criada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()


if __name__ == "__main__":
    print("=" * 70)
    print("REDEFININDO CARGOS E PERMISSÕES")
    print("=" * 70)
    
    redefinir_cargos_e_permissoes()
    
    print("\n" + "=" * 70)
    print("CRIANDO TABELA DE MUDANÇA DE CARGO")
    print("=" * 70)
    
    criar_tabela_solicitacoes_mudanca_cargo()
