import sqlite3
import os

CAMINHO_BANCO = "data/projetos_sonae.db"

def criar_tabela_relatorios():
    """
    Cria a tabela de relatórios salvos pelos usuários.
    Preparada para futura implementação de sistema de usuários.
    """
    conexao = None
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        # Criar tabela de relatórios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relatorios_salvos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_relatorio TEXT NOT NULL,
                arquivo_original TEXT,
                conteudo_relatorio TEXT NOT NULL,
                tags TEXT,
                data_criacao TEXT NOT NULL,
                user_id INTEGER DEFAULT NULL,
                tamanho_detalhe TEXT,
                prompt_personalizado TEXT,
                FOREIGN KEY (user_id) REFERENCES usuarios(id)
            )
        """)
        
        print("✅ Tabela 'relatorios_salvos' criada com sucesso!")
        
        # Criar índice para melhor performance nas consultas por usuário
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relatorios_user 
            ON relatorios_salvos(user_id)
        """)
        
        # Criar índice para busca por data
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relatorios_data 
            ON relatorios_salvos(data_criacao)
        """)
        
        print("✅ Índices criados com sucesso!")
        
        conexao.commit()
        print("\n🎉 Banco de dados preparado para salvar relatórios!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()

if __name__ == "__main__":
    criar_tabela_relatorios()
