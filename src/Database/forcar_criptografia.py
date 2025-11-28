"""Força criptografia de todos os dados"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Readers.criptograph import encriptar_dado

CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")

conexao = sqlite3.connect(CAMINHO_BANCO)
cursor = conexao.cursor()

cursor.execute("SELECT id, responsavel FROM projetos")
todos = cursor.fetchall()

print(f"Criptografando {len(todos)} registros...\n")

for id_proj, resp in todos:
    if resp:
        cripto = encriptar_dado(resp)
        cursor.execute("UPDATE projetos SET responsavel = ? WHERE id = ?", (cripto, id_proj))
        print(f"✅ ID {id_proj}: '{resp}' → CRIPTOGRAFADO")

conexao.commit()
conexao.close()
print("\n✅ Todos os dados foram criptografados!")
