import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os

CAMINHO_BANCO = "data/projetos_sonae.db"

class RelatoriosDB:
    """Gerenciador de relatórios salvos no banco de dados"""
    
    def __init__(self):
        self.caminho_banco = CAMINHO_BANCO
    
    def salvar_relatorio(
        self, 
        nome_relatorio: str, 
        conteudo_relatorio: str,
        arquivo_original: str = None,
        tags: List[str] = None,
        tamanho_detalhe: str = None,
        prompt_personalizado: str = None,
        user_id: int = None
    ) -> bool:
        """
        Salva um relatório no banco de dados.
        
        Args:
            nome_relatorio: Nome do relatório
            conteudo_relatorio: Conteúdo completo do relatório
            arquivo_original: Nome do arquivo original que foi processado
            tags: Lista de tags para categorização
            tamanho_detalhe: Nível de detalhe usado (Curto, Médio, Longo, etc)
            prompt_personalizado: Prompt personalizado usado (se houver)
            user_id: ID do usuário (para futuro sistema de login)
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            # Converter tags para string
            tags_str = ", ".join(tags) if tags else None
            
            # Data atual
            data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO relatorios_salvos 
                (nome_relatorio, arquivo_original, conteudo_relatorio, tags, 
                 data_criacao, user_id, tamanho_detalhe, prompt_personalizado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome_relatorio,
                arquivo_original,
                conteudo_relatorio,
                tags_str,
                data_criacao,
                user_id,
                tamanho_detalhe,
                prompt_personalizado
            ))
            
            conexao.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar relatório: {e}")
            if conexao:
                conexao.rollback()
            return False
            
        finally:
            if conexao:
                conexao.close()
    
    def listar_relatorios(self, user_id: int = None, limite: int = 50) -> List[Dict]:
        """
        Lista os relatórios salvos.
        
        Args:
            user_id: Se fornecido, filtra por usuário (para futuro sistema de login)
            limite: Número máximo de relatórios a retornar
        
        Returns:
            Lista de dicionários com os dados dos relatórios
        """
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            if user_id is not None:
                # Filtrar por usuário
                cursor.execute("""
                    SELECT * FROM relatorios_salvos 
                    WHERE user_id = ? OR user_id IS NULL
                    ORDER BY data_criacao DESC
                    LIMIT ?
                """, (user_id, limite))
            else:
                # Por enquanto, retorna todos (até implementar login)
                cursor.execute("""
                    SELECT * FROM relatorios_salvos 
                    ORDER BY data_criacao DESC
                    LIMIT ?
                """, (limite,))
            
            rows = cursor.fetchall()
            relatorios = []
            
            for row in rows:
                relatorios.append({
                    'id': row['id'],
                    'nome_relatorio': row['nome_relatorio'],
                    'arquivo_original': row['arquivo_original'],
                    'conteudo_relatorio': row['conteudo_relatorio'],
                    'tags': row['tags'],
                    'data_criacao': row['data_criacao'],
                    'tamanho_detalhe': row['tamanho_detalhe'],
                    'prompt_personalizado': row['prompt_personalizado']
                })
            
            return relatorios
            
        except Exception as e:
            print(f"Erro ao listar relatórios: {e}")
            return []
            
        finally:
            if conexao:
                conexao.close()
    
    def buscar_relatorio_por_id(self, relatorio_id: int) -> Optional[Dict]:
        """
        Busca um relatório específico pelo ID.
        
        Args:
            relatorio_id: ID do relatório
        
        Returns:
            Dicionário com os dados do relatório ou None se não encontrado
        """
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT * FROM relatorios_salvos WHERE id = ?
            """, (relatorio_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'nome_relatorio': row['nome_relatorio'],
                    'arquivo_original': row['arquivo_original'],
                    'conteudo_relatorio': row['conteudo_relatorio'],
                    'tags': row['tags'],
                    'data_criacao': row['data_criacao'],
                    'tamanho_detalhe': row['tamanho_detalhe'],
                    'prompt_personalizado': row['prompt_personalizado']
                }
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar relatório: {e}")
            return None
            
        finally:
            if conexao:
                conexao.close()
    
    def deletar_relatorio(self, relatorio_id: int, user_id: int = None) -> bool:
        """
        Deleta um relatório.
        
        Args:
            relatorio_id: ID do relatório a deletar
            user_id: ID do usuário (para validação futura)
        
        Returns:
            bool: True se deletou com sucesso
        """
        conexao = None
        try:
            conexao = sqlite3.connect(self.caminho_banco)
            cursor = conexao.cursor()
            
            if user_id is not None:
                # Quando tiver login, só permite deletar se for do usuário
                cursor.execute("""
                    DELETE FROM relatorios_salvos 
                    WHERE id = ? AND (user_id = ? OR user_id IS NULL)
                """, (relatorio_id, user_id))
            else:
                cursor.execute("""
                    DELETE FROM relatorios_salvos WHERE id = ?
                """, (relatorio_id,))
            
            conexao.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erro ao deletar relatório: {e}")
            if conexao:
                conexao.rollback()
            return False
            
        finally:
            if conexao:
                conexao.close()
