import sqlite3

conn = sqlite3.connect('data/projetos_sonae.db')
cursor = conn.cursor()
cursor.execute('SELECT id, nome_projeto, resumo_executivo, principais_desafios, resumo_ia FROM projetos')
projetos = cursor.fetchall()

print('\n' + '='*80)
print('PROJETOS NO BANCO:')
print('='*80)

for id, nome, resumo, desafios, ia in projetos:
    print(f'\nID {id}: {nome}')
    print(f'  Resumo Executivo: {resumo[:100] if resumo else "NULL"}...')
    print(f'  Principais Desafios: {desafios[:100] if desafios else "NULL"}...')
    print(f'  Insight IA: {ia[:100] if ia else "NULL"}...')

conn.close()
