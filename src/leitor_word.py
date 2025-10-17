# Passo 1: Importar a função "Document" da biblioteca docx
import docx

# Passo 2: Definir o caminho para o nosso arquivo do Word
caminho_arquivo = "data/relatorio_crm.docx"

# Passo 3: Abrir e ler o conteúdo do arquivo
try:
    # A função Document() abre o arquivo do Word na memória
    documento = docx.Document(caminho_arquivo)

    print("Arquivo Word lido com sucesso! Aqui está o texto extraído:")
    print("-" * 60) # Apenas para criar uma linha de separação

    # Um documento do Word é composto por parágrafos.
    # Vamos passar por cada parágrafo e imprimir o texto dele.
    for paragrafo in documento.paragraphs:
        # A propriedade .text pega apenas o texto do parágrafo, ignorando formatação
        print(paragrafo.text)
    
    print("-" * 60)

except Exception as e:
    # Usamos "Exception as e" para capturar qualquer tipo de erro
    # e imprimir a mensagem de erro específica.
    print(f"ERRO: Não foi possível ler o arquivo. Detalhes: {e}")