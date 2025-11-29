import pandas as pd
import sqlite3
import os
import sys
# Importamos a função de segurança
from Readers.criptograph import encriptar_dado

# Adicionar path para importar processador de IA
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from AI.processador_ia import gerar_insight_para_projeto

CAMINHO_ARQUIVO_EXCEL = "data/relatorios_sonae.xlsx"
CAMINHO_BANCO = "data/projetos_sonae.db"


def ler_excel(caminho_arquivo):
    """
    Lê um arquivo Excel e retorna todo o texto extraído.
    
    Args:
        caminho_arquivo: Caminho para o arquivo Excel (.xlsx, .xls)
        
    Returns:
        String contendo todo o conteúdo do Excel formatado
    """
    try:
        # Ler todas as planilhas
        excel_file = pd.ExcelFile(caminho_arquivo)
        texto_completo = ""
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(caminho_arquivo, sheet_name=sheet_name)
            texto_completo += f"\n=== Planilha: {sheet_name} ===\n"
            texto_completo += df.to_string() + "\n"
        
        return texto_completo
        
    except Exception as e:
        print(f"Erro ao ler Excel: {e}")
        return None


def processar_dados_excel():
    conexao = None
    try:
        # --- ETAPA 1: LER O EXCEL ---
        # header=1 porque a primeira linha do seu Excel é vazia/título
        dataframe = pd.read_excel(CAMINHO_ARQUIVO_EXCEL, header=1)
        print(f"Arquivo '{CAMINHO_ARQUIVO_EXCEL}' lido com sucesso.")

        # --- ETAPA 2: CONECTAR AO BANCO ---
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        print(f"Conexão com o banco '{CAMINHO_BANCO}' estabelecida.")

        print("Iniciando lógica UPSERT com Criptografia...")
        linhas_atualizadas = 0
        linhas_inseridas = 0

        for index, linha in dataframe.iterrows():
            nome = linha['Nome do Projeto']
            status = linha['Status']
            # AQUI APLICAMOS A SEGURANÇA:
            responsavel_bruto = linha['Responsavel']
            responsavel_seguro = encriptar_dado(responsavel_bruto)
            
            data_atualizacao = str(linha['Ultima Atualizacao'])
            fonte = CAMINHO_ARQUIVO_EXCEL
            
            # Extrair campos detalhados (se existirem no Excel)
            resumo_executivo = linha.get('Resumo Executivo', 
                'Projeto focado na extração, transformação e análise de dados empresariais '
                'para suporte à tomada de decisão estratégica. Implementa processos automatizados '
                'de ETL (Extract, Transform, Load) para consolidação de informações de múltiplas '
                'fontes de dados, incluindo sistemas legados, APIs externas e planilhas operacionais.')
            
            progresso_atual = linha.get('Progresso Atual', 
                'Fase de desenvolvimento em andamento. Arquitetura de dados definida e validada, '
                'com implementação de 60% dos pipelines de extração. Testes unitários em execução '
                'para garantir qualidade e integridade dos dados processados.')
            
            principais_desafios = linha.get('Principais Desafios', 
                'Integração com múltiplas fontes de dados heterogêneas, garantindo consistência '
                'e qualidade da informação. Necessidade de otimização de performance para processar '
                'grandes volumes de dados em tempo hábil. Padronização de formatos e estruturas '
                'de dados provenientes de sistemas distintos.')
            
            acoes_corretivas = linha.get('Ações Corretivas', 
                'Revisão da arquitetura de dados para melhorar escalabilidade. Implementação de '
                'camada de cache para otimizar consultas frequentes. Criação de documentação técnica '
                'detalhada para facilitar manutenção e evolução do sistema.')
            
            perspectiva = linha.get('Perspectiva', 
                'Lançamento da versão beta previsto para o próximo trimestre, com foco em validação '
                'junto aos usuários-chave. Expectativa de redução de 40% no tempo de geração de '
                'relatórios gerenciais. Planejamento de expansão para incluir análises preditivas '
                'utilizando machine learning.')

            # --- ETAPA 3: VERIFICAR SE O PROJETO JÁ EXISTE ---
            cursor.execute("SELECT id FROM projetos WHERE nome_projeto = ?", (nome,))
            projeto_existente = cursor.fetchone()

            if projeto_existente:
                # --- UPDATE ---
                id_projeto = projeto_existente[0]
                sql_update = """
                UPDATE projetos 
                SET responsavel = ?, status = ?, data_ultima_atualizacao = ?, fonte_dados = ?,
                    resumo_executivo = ?, progresso_atual = ?, principais_desafios = ?,
                    acoes_corretivas = ?, perspectiva = ?
                WHERE id = ?
                """
                cursor.execute(sql_update, (responsavel_seguro, status, data_atualizacao, fonte,
                                           resumo_executivo, progresso_atual, principais_desafios,
                                           acoes_corretivas, perspectiva, id_projeto))
                linhas_atualizadas += 1
                
                # Gerar insight de IA
                print(f"  Gerando insight de IA para '{nome}'...")
                gerar_insight_para_projeto(projeto_id=id_projeto)
            else:
                # --- INSERT ---
                sql_insert = """
                INSERT INTO projetos (nome_projeto, responsavel, status, data_ultima_atualizacao, fonte_dados,
                                     resumo_executivo, progresso_atual, principais_desafios,
                                     acoes_corretivas, perspectiva)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                cursor.execute(sql_insert, (nome, responsavel_seguro, status, data_atualizacao, fonte,
                                           resumo_executivo, progresso_atual, principais_desafios,
                                           acoes_corretivas, perspectiva))
                linhas_inseridas += 1
                
                # Obter ID do projeto recém-inserido e gerar insight
                novo_id = cursor.lastrowid
                print(f"  Gerando insight de IA para '{nome}'...")
                gerar_insight_para_projeto(projeto_id=novo_id)

        # --- ETAPA 5: SALVAR ---
        conexao.commit()
        print(f"Sucesso! {linhas_inseridas} linhas novas inseridas.")
        print(f"Sucesso! {linhas_atualizadas} linhas existentes foram atualizadas.")

    except Exception as e:
        print(f"ERRO inesperado ao processar Excel: {e}")
        if conexao:
            conexao.rollback()
            
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    processar_dados_excel()