import sqlite3
from datetime import datetime

CAMINHO_BANCO = "data/projetos_sonae.db"

def adicionar_colunas_projetos():
    """
    Adiciona colunas necessárias para criação de projetos via interface.
    """
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        print("=" * 70)
        print("ATUALIZANDO ESTRUTURA DA TABELA PROJETOS")
        print("=" * 70)
        
        # Lista de colunas a adicionar (se não existirem)
        colunas_novas = [
            ("nome", "TEXT"),
            ("data_inicio", "TEXT"),
            ("data_fim", "TEXT"),
            ("prioridade", "TEXT DEFAULT 'Média'"),
            ("orcamento", "REAL DEFAULT 0.0"),
            ("custo_atual", "REAL DEFAULT 0.0"),
            ("progresso", "INTEGER DEFAULT 0"),
            ("descricao", "TEXT"),
            ("categoria", "TEXT"),
            ("tags", "TEXT"),
            ("criado_em", "TEXT"),
            ("criado_por", "INTEGER"),
        ]
        
        # Verificar quais colunas já existem
        cursor.execute("PRAGMA table_info(projetos)")
        colunas_existentes = [row[1] for row in cursor.fetchall()]
        
        print(f"\n📋 Colunas existentes: {', '.join(colunas_existentes)}\n")
        
        # Adicionar colunas que não existem
        colunas_adicionadas = []
        for coluna, tipo in colunas_novas:
            if coluna not in colunas_existentes:
                try:
                    cursor.execute(f"ALTER TABLE projetos ADD COLUMN {coluna} {tipo}")
                    colunas_adicionadas.append(coluna)
                    print(f"✅ Coluna '{coluna}' adicionada ({tipo})")
                except Exception as e:
                    print(f"⚠️  Erro ao adicionar '{coluna}': {e}")
        
        # Migrar dados existentes
        if 'nome' not in colunas_existentes and 'nome_projeto' in colunas_existentes:
            print("\n🔄 Migrando dados de 'nome_projeto' para 'nome'...")
            cursor.execute("UPDATE projetos SET nome = nome_projeto WHERE nome IS NULL")
            print("✅ Migração concluída")
        
        conexao.commit()
        
        print("\n" + "=" * 70)
        if colunas_adicionadas:
            print(f"✅ {len(colunas_adicionadas)} colunas adicionadas com sucesso!")
            print(f"   Colunas: {', '.join(colunas_adicionadas)}")
        else:
            print("✅ Tabela já está atualizada!")
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
    adicionar_colunas_projetos()
