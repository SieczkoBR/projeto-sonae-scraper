# No seu src/limpa_banco.py
import sqlite3
import os

CAMINHO_BANCO = "data/projetos_sonae.db"
conexao = None
try:
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    print("Conectado ao banco de dados...")
    
    # O comando correto: apaga CUIDADOSAMENTE qualquer linha onde
    # o 'nome_projeto' é NULO (NULL) ou é um texto VAZIO ('').
    sql_delete = "DELETE FROM projetos WHERE nome_projeto IS NULL OR nome_projeto = '';"
    
    cursor.execute(sql_delete)
    conexao.commit()
    
    print(f"Limpeza cirúrgica concluída! {cursor.rowcount} linhas 'fantasmas' (sem nome) foram removidas.")

except Exception as e:
    print(f"ERRO ao limpar o banco: {e}")
    
finally:
    if conexao:
        conexao.close()
        print("Conexão fechada.")