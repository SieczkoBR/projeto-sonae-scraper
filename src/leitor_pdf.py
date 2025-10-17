# Passo 1: Importar a classe PdfReader da biblioteca PyPDF2
from PyPDF2 import PdfReader

# Passo 2: Definir o caminho para o nosso arquivo PDF
caminho_arquivo = "data/relatorio_riscos.pdf"

# Passo 3: Abrir, ler o conteúdo e fechar o arquivo
try:
    # Criamos um objeto leitor para o nosso PDF
    leitor = PdfReader(caminho_arquivo)
    
    print(f"Arquivo PDF lido com sucesso! O documento tem {len(leitor.pages)} página(s).")
    print("-" * 60)

    # Vamos passar por cada página do PDF
    # enumerate nos dá tanto o número da página (i) quanto a página em si (page)
    for i, pagina in enumerate(leitor.pages):
        # Extrai o texto da página atual
        texto = pagina.extract_text()
        print(f"--- TEXTO DA PÁGINA {i + 1} ---")
        print(texto)

    print("-" * 60)

except Exception as e:
    print(f"ERRO: Não foi possível ler o arquivo PDF. Detalhes: {e}")