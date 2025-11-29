from cryptography.fernet import Fernet
import os

# Caminho ABSOLUTO para a chave na raiz do projeto
RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARQUIVO_CHAVE = os.path.join(RAIZ_PROJETO, "secret.key")

def carregar_chave():
    """
    Carrega a chave secreta do arquivo. Se não existir, cria uma nova.
    """
    if not os.path.exists(ARQUIVO_CHAVE):
        chave = Fernet.generate_key()
        with open(ARQUIVO_CHAVE, "wb") as key_file:
            key_file.write(chave)
        print(f"NOVA CHAVE DE SEGURANÇA GERADA em: {ARQUIVO_CHAVE}")
        print("   Não perca este arquivo!")
    else:
        with open(ARQUIVO_CHAVE, "rb") as key_file:
            chave = key_file.read()
    return chave

# Criamos o objeto "fernet" (o nosso codificador)
chave = carregar_chave()
fernet = Fernet(chave)

def encriptar_dado(dado_texto):
    """Recebe texto (ex: 'Ana Costa') e retorna criptografado (ex: 'gAAAA...')."""
    if not dado_texto:
        return None
    # O Fernet precisa de bytes, então convertemos o texto
    dado_bytes = str(dado_texto).encode()
    dado_encriptado = fernet.encrypt(dado_bytes)
    return dado_encriptado.decode() # Retorna como string para salvar no banco

def decriptar_dado(dado_encriptado):
    """Recebe texto criptografado e retorna o original."""
    if not dado_encriptado:
        return None
    try:
        dado_bytes = str(dado_encriptado).encode()
        dado_decriptado = fernet.decrypt(dado_bytes)
        return dado_decriptado.decode()
    except Exception:
        return "Erro: Chave inválida"