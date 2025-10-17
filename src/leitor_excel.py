# Passo 1: Importar a biblioteca Pandas e dar um "apelido" para ela de "pd"
import pandas as pd

# Passo 2: Definir o caminho onde está nosso arquivo Excel
# Os ".." significam "volte uma pasta para trás"
# Então saímos de 'src', voltamos para a raiz do projeto, e entramos em 'data'
caminho_arquivo = "data/relatorios_sonae.xlsx"

# Passo 3: Usar o pandas para ler o arquivo Excel
# O try/except é uma forma segura de lidar com erros.
# Se o arquivo não for encontrado, ele nos dará uma mensagem amigável.
try:
    # pd.read_excel lê o arquivo e guarda os dados em uma variável chamada "dataframe"
    # Um DataFrame é basicamente uma tabela de dados na memória do computador.
    dataframe = pd.read_excel(caminho_arquivo)

    # Passo 4: Imprimir a tabela no terminal para vermos se funcionou
    print("Arquivo Excel lido com sucesso! Aqui estão os dados:")
    print(dataframe)

except FileNotFoundError:
    print(f"ERRO: O arquivo não foi encontrado no caminho: {caminho_arquivo}")
    print("Verifique se o nome do arquivo e da pasta estão corretos.")