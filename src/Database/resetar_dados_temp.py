"""Script temporário para resetar dados criptografados"""
import sqlite3
import os

CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")

conexao = sqlite3.connect(CAMINHO_BANCO)
cursor = conexao.cursor()

# Buscar dados atuais
cursor.execute("SELECT id, responsavel FROM projetos")
dados = cursor.fetchall()

print("Dados atuais:")
for id_proj, resp in dados:
    print(f"  ID {id_proj}: {resp[:50]}...")

# Resetar para texto plano (baseado nas imagens que você mostrou)
updates = [
    (7, "Joana (Operações)"),
    (8, "Joana (Operações)"),
    (9, "Joana (Operações)"),
    (10, "Equipe CRM")
]

for id_proj, nome_real in updates:
    cursor.execute("UPDATE projetos SET responsavel = ? WHERE id = ?", (nome_real, id_proj))
    print(f"✅ ID {id_proj} resetado para: {nome_real}")

conexao.commit()
conexao.close()
print("\n✅ Dados resetados com sucesso!")
