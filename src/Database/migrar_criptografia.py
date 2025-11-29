"""
Script de Migração: Criptografa todos os dados sensíveis existentes no banco
Execute UMA VEZ para proteger dados antigos
"""
import sqlite3
import os
import sys

# Adicionar caminho para importar o módulo de criptografia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from Readers.criptograph import encriptar_dado, decriptar_dado

CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")

def verificar_se_esta_criptografado(texto):
    """Tenta descriptografar. Se der erro, não está criptografado"""
    if not texto or texto.strip() == '':
        return True  # Vazio não precisa criptografar
    
    try:
        decriptar_dado(texto)
        return True  # Conseguiu descriptografar = já está criptografado
    except:
        return False  # Não conseguiu = texto plano

def migrar_dados_existentes():
    """Criptografa todos os campos 'responsavel' que ainda estão em texto plano"""
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        
        print("🔍 Buscando dados não criptografados...")
        
        # Buscar todos os registros
        cursor.execute("SELECT id, responsavel FROM projetos")
        todos_projetos = cursor.fetchall()
        
        if not todos_projetos:
            print("⚠️  Nenhum projeto encontrado no banco.")
            return
        
        print(f"📊 Total de projetos no banco: {len(todos_projetos)}")
        
        registros_atualizados = 0
        registros_ja_criptografados = 0
        
        for projeto_id, responsavel in todos_projetos:
            if not responsavel:
                continue
            
            # Verificar se já está criptografado
            if verificar_se_esta_criptografado(responsavel):
                registros_ja_criptografados += 1
                print(f"  ✓ ID {projeto_id}: Já criptografado")
                continue
            
            # Criptografar e atualizar
            responsavel_criptografado = encriptar_dado(responsavel)
            cursor.execute(
                "UPDATE projetos SET responsavel = ? WHERE id = ?",
                (responsavel_criptografado, projeto_id)
            )
            registros_atualizados += 1
            print(f"  🔐 ID {projeto_id}: '{responsavel}' → CRIPTOGRAFADO")
        
        # Salvar mudanças
        conexao.commit()
        
        print("\n" + "="*60)
        print(f"✅ Migração concluída!")
        print(f"   • Registros já criptografados: {registros_ja_criptografados}")
        print(f"   • Registros recém-criptografados: {registros_atualizados}")
        print(f"   • Total processado: {len(todos_projetos)}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        if conexao:
            conexao.rollback()
    
    finally:
        if conexao:
            conexao.close()
            print("🔒 Conexão com o banco fechada.")

if __name__ == "__main__":
    print("="*60)
    print("🔐 SCRIPT DE MIGRAÇÃO - CRIPTOGRAFIA DE DADOS SENSÍVEIS")
    print("="*60)
    print("\n⚠️  ATENÇÃO: Este script irá criptografar TODOS os dados")
    print("   sensíveis (campo 'responsavel') no banco de dados.\n")
    
    resposta = input("Deseja continuar? (s/N): ").strip().lower()
    
    if resposta in ['s', 'sim', 'yes', 'y']:
        print("\n🚀 Iniciando migração...\n")
        migrar_dados_existentes()
    else:
        print("\n❌ Migração cancelada pelo usuário.")
