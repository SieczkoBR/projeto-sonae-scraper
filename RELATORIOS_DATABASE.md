# 📊 Sistema de Relatórios - Documentação

## ✅ Funcionalidades Implementadas

### 1. Salvamento de Relatórios
- ✅ Relatórios gerados pela IA podem ser salvos no banco de dados
- ✅ Campos salvos:
  - Nome do relatório
  - Conteúdo completo
  - Arquivo original processado
  - Tags para categorização
  - Nível de detalhe usado
  - Prompt personalizado (se houver)
  - Data de criação
  - **user_id** (preparado para futuro sistema de login)

### 2. Listagem de Relatórios
- ✅ Histórico completo substituindo placeholders
- ✅ Visualização de relatórios salvos
- ✅ Filtros por data (mais recentes primeiro)
- ✅ Exibição de detalhes completos
- ✅ Funcionalidade de deletar relatórios

### 3. Estrutura do Banco de Dados

#### Tabela: `relatorios_salvos`
```sql
CREATE TABLE relatorios_salvos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_relatorio TEXT NOT NULL,
    arquivo_original TEXT,
    conteudo_relatorio TEXT NOT NULL,
    tags TEXT,
    data_criacao TEXT NOT NULL,
    user_id INTEGER DEFAULT NULL,          -- Preparado para sistema de usuários
    tamanho_detalhe TEXT,
    prompt_personalizado TEXT,
    FOREIGN KEY (user_id) REFERENCES usuarios(id)
)
```

#### Índices para Performance
- `idx_relatorios_user`: Otimiza buscas por usuário
- `idx_relatorios_data`: Otimiza ordenação por data

---

## 🚀 Próxima Fase: Sistema de Usuários

### Estrutura Preparada

O sistema já está preparado para implementação de login com permissões:

#### 1. Campo `user_id`
- Todos os relatórios têm campo `user_id` (atualmente NULL)
- Quando implementar login, cada relatório será associado ao usuário criador

#### 2. Funcionalidades Futuras Planejadas

##### Sistema de Usuários
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    nome_completo TEXT,
    nivel_permissao TEXT DEFAULT 'usuario',  -- 'admin', 'gestor', 'usuario'
    data_criacao TEXT NOT NULL,
    ativo INTEGER DEFAULT 1
)
```

##### Níveis de Permissão
1. **Admin**
   - Acesso a todos os relatórios
   - Gerenciamento de usuários
   - Configurações do sistema

2. **Gestor**
   - Acesso aos próprios relatórios
   - Acesso aos relatórios da equipe
   - Criação e edição de relatórios

3. **Usuário**
   - Acesso apenas aos próprios relatórios
   - Criação de relatórios
   - Leitura somente

### Como Implementar Login (Roadmap)

#### Etapa 1: Criar Tabela de Usuários
```python
# src/Database/criar_tabela_usuarios.py
import sqlite3
import hashlib

def criar_tabela_usuarios():
    conexao = sqlite3.connect("data/projetos_sonae.db")
    cursor = conexao.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            nome_completo TEXT,
            nivel_permissao TEXT DEFAULT 'usuario',
            data_criacao TEXT NOT NULL,
            ativo INTEGER DEFAULT 1
        )
    """)
    
    conexao.commit()
    conexao.close()
```

#### Etapa 2: Implementar Sistema de Login
```python
# src/Auth/autenticacao.py
import streamlit as st
import hashlib
import sqlite3
from datetime import datetime

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_login(username, senha):
    conexao = sqlite3.connect("data/projetos_sonae.db")
    cursor = conexao.cursor()
    
    senha_hash = hash_senha(senha)
    cursor.execute("""
        SELECT id, username, nome_completo, nivel_permissao 
        FROM usuarios 
        WHERE username = ? AND senha_hash = ? AND ativo = 1
    """, (username, senha_hash))
    
    usuario = cursor.fetchone()
    conexao.close()
    
    return usuario

def tela_login():
    st.title("🔐 Login")
    
    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        usuario = verificar_login(username, senha)
        if usuario:
            st.session_state['user_id'] = usuario[0]
            st.session_state['username'] = usuario[1]
            st.session_state['nome_completo'] = usuario[2]
            st.session_state['nivel_permissao'] = usuario[3]
            st.success(f"Bem-vindo, {usuario[2]}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
```

#### Etapa 3: Modificar `relatorios_db.py`
```python
# Já está preparado! Só precisa passar o user_id ao salvar:

db.salvar_relatorio(
    nome_relatorio=nome,
    conteudo_relatorio=relatorio,
    user_id=st.session_state.get('user_id')  # Pega do session_state
)

# E filtrar na listagem:
relatorios = db.listar_relatorios(
    user_id=st.session_state.get('user_id')
)
```

#### Etapa 4: Adicionar Controle de Acesso
```python
# src/Auth/permissoes.py

def pode_visualizar_relatorio(relatorio, user_id, nivel_permissao):
    """Verifica se usuário pode visualizar o relatório"""
    if nivel_permissao == 'admin':
        return True
    
    if relatorio['user_id'] == user_id:
        return True
    
    # Gestor pode ver relatórios da equipe (implementar lógica de equipe)
    if nivel_permissao == 'gestor':
        # TODO: Verificar se usuário está na mesma equipe
        pass
    
    return False

def pode_deletar_relatorio(relatorio, user_id, nivel_permissao):
    """Verifica se usuário pode deletar o relatório"""
    if nivel_permissao == 'admin':
        return True
    
    if relatorio['user_id'] == user_id:
        return True
    
    return False
```

---

## 📝 Arquivos Modificados/Criados

### Criados
1. ✅ `src/Database/criar_tabela_relatorios.py` - Script para criar tabela
2. ✅ `src/Database/relatorios_db.py` - Gerenciador de relatórios
3. ✅ `RELATORIOS_DATABASE.md` - Esta documentação

### Modificados
1. ✅ `src/Components/Pages/custom_summary.py` - Integração com banco de dados

### Próximos Passos (Login)
1. ⏳ `src/Database/criar_tabela_usuarios.py`
2. ⏳ `src/Auth/autenticacao.py`
3. ⏳ `src/Auth/permissoes.py`
4. ⏳ `src/app.py` - Adicionar verificação de login

---

## 🔧 Como Usar

### Salvar Relatório
1. Gere um relatório usando a IA
2. Preencha o nome desejado
3. Adicione tags (opcional)
4. Clique em "💾 Salvar no Histórico"

### Visualizar Relatórios Salvos
1. Expanda "📚 Histórico de Relatórios Gerados"
2. Veja a tabela com todos os relatórios
3. Selecione um relatório para visualizar detalhes
4. Opcionalmente, delete relatórios antigos

---

## 🎯 Benefícios da Estrutura Atual

✅ **Fácil migração para multi-usuário**: Campo `user_id` já existe
✅ **Performance otimizada**: Índices já criados
✅ **Separação de responsabilidades**: Módulo `relatorios_db.py` centraliza a lógica
✅ **Preparado para Foreign Keys**: Relação com tabela `usuarios` já definida
✅ **Sem placeholders**: Dados reais do banco de dados

---

## 📊 Estatísticas

- **Relatórios podem ser:** Salvos, Listados, Visualizados, Deletados
- **Tags suportadas:** Ilimitadas, separadas por vírgula
- **Limite de listagem:** 20 relatórios (configurável)
- **Formato de data:** DD/MM/YYYY HH:MM:SS

---

**Última atualização:** 28/11/2025
**Status:** ✅ Produção (sem sistema de usuários)
**Próximo passo:** 🔐 Implementar autenticação e permissões
