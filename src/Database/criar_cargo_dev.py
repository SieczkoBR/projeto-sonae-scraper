import sqlite3

CAMINHO_BANCO = "data/projetos_sonae.db"

def criar_cargo_desenvolvedor():
    """
    Cria o cargo 'Desenvolvedor' e atualiza os níveis hierárquicos de todos os cargos.
    
    CÁLCULO DE NÍVEIS HIERÁRQUICOS:
    - Total de permissões: 15
    - Pontos por permissão: 100 ÷ 15 = 6.67
    - Admin: 15 permissões = 100 (exceção - sempre 100)
    - Desenvolvedor: 11 permissões = 73
    - Gestor: 11 permissões = 73
    - Analista: 8 permissões = 53
    - Visualizador: 4 permissões = 27
    """
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        print("=" * 70)
        print("CRIANDO CARGO DESENVOLVEDOR E ATUALIZANDO NÍVEIS HIERÁRQUICOS")
        print("=" * 70)
        
        # 1. Criar/Atualizar cargo Desenvolvedor
        print("\n📝 Criando cargo Desenvolvedor...")
        cursor.execute("""
            INSERT OR REPLACE INTO cargos (codigo, nome, descricao, nivel_hierarquia)
            VALUES (?, ?, ?, ?)
        """, (
            'desenvolvedor',
            'Desenvolvedor',
            'Acesso completo a funcionalidades do sistema exceto administração de usuários',
            73
        ))
        
        # 2. Atualizar níveis hierárquicos dos outros cargos
        print("📊 Atualizando níveis hierárquicos...")
        
        niveis = [
            ('admin', 100),           # 15 permissões - exceção
            ('desenvolvedor', 73),    # 11 permissões
            ('gestor', 73),           # 11 permissões
            ('analista', 53),         # 8 permissões
            ('visualizador', 27),     # 4 permissões
        ]
        
        for codigo, nivel in niveis:
            cursor.execute("""
                UPDATE cargos SET nivel_hierarquia = ? WHERE codigo = ?
            """, (nivel, codigo))
        
        # 3. Adicionar permissões ao Desenvolvedor
        print("🔑 Definindo permissões do Desenvolvedor...")
        
        # Permissões do Desenvolvedor (11 total - todas exceto as 4 de admin)
        permissoes_dev = [
            'view_dashboard',      # Visualizar Dashboard
            'view_projects',       # Visualizar Projetos
            'view_reports',        # Visualizar Relatórios
            'view_ai_insights',    # Visualizar Insights IA
            'create_reports',      # Criar Relatórios
            'edit_projects',       # Editar Projetos
            'delete_projects',     # Deletar Projetos
            'delete_reports',      # Deletar Relatórios
            'upload_files',        # Upload de Arquivos
            'import_data',         # Importar Dados
            'view_logs',           # Visualizar Logs
            # NÃO TEM:
            # - approve_accounts (admin)
            # - manage_users (admin)
            # - manage_permissions (admin)
            # - system_config (admin)
        ]
        
        # Remover permissões antigas do desenvolvedor (se existir)
        cursor.execute("DELETE FROM cargo_permissoes WHERE cargo_codigo = 'desenvolvedor'")
        
        # Adicionar permissões
        for perm_codigo in permissoes_dev:
            cursor.execute("""
                INSERT INTO cargo_permissoes (cargo_codigo, permissao_codigo)
                VALUES ('desenvolvedor', ?)
            """, (perm_codigo,))
        
        conexao.commit()
        
        # 4. Exibir resumo
        print("\n" + "=" * 70)
        print("✅ CARGO DESENVOLVEDOR CRIADO COM SUCESSO!")
        print("=" * 70)
        
        print("\n📋 RESUMO DOS CARGOS E NÍVEIS HIERÁRQUICOS:\n")
        
        cursor.execute("""
            SELECT c.nome, c.nivel_hierarquia, COUNT(cp.permissao_codigo) as num_perms
            FROM cargos c
            LEFT JOIN cargo_permissoes cp ON c.codigo = cp.cargo_codigo
            GROUP BY c.id
            ORDER BY c.nivel_hierarquia DESC
        """)
        
        for i, row in enumerate(cursor.fetchall(), 1):
            nome, nivel, num_perms = row
            print(f"{i}. {nome}")
            print(f"   Nível Hierárquico: {nivel}")
            print(f"   Permissões: {num_perms}")
            print()
        
        print("=" * 70)
        print("📊 CÁLCULO: 100 pontos ÷ 15 permissões = 6.67 pontos/permissão")
        print("⚠️  Admin sempre = 100 (exceção à regra)")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        if conexao:
            conexao.rollback()
        raise
    finally:
        if conexao:
            conexao.close()


if __name__ == "__main__":
    criar_cargo_desenvolvedor()
