# 🔐 Sistema de Segurança de Dados

## Visão Geral

O sistema implementa **criptografia em repouso** para proteger dados sensíveis no banco de dados, enquanto mantém a **usabilidade** no frontend.

---

## 🔄 Fluxo de Dados

### **1. ENTRADA DE DADOS (ETL) - CRIPTOGRAFIA**

Quando dados são importados de fontes externas:

```
Excel/PDF/Word → Leitor (src/Readers/) → CRIPTOGRAFA → SQLite (data/projetos_sonae.db)
```

**Arquivos responsáveis:**
- `src/Readers/leitor_excel.py` - Importa dados do Excel
- `src/Readers/leitor_pdf.py` - Importa dados do PDF
- `src/Readers/leitor_word.py` - Importa dados do Word
- `src/Readers/criptograph.py` - Módulo de criptografia (Fernet)

**Campo criptografado:**
- `responsavel` - Nome do responsável pelo projeto

### **2. ARMAZENAMENTO - PROTEGIDO**

No banco de dados SQLite (`data/projetos_sonae.db`):

```sql
-- Exemplo de registro no banco
id | nome_projeto | responsavel (CRIPTOGRAFADO) | status
1  | Projeto CRM  | gAAAAABpIam0M...              | Em Andamento
```

### **3. EXIBIÇÃO (FRONTEND) - DESCRIPTOGRAFIA**

Quando dados são exibidos na interface:

```
SQLite → Sidebar.carregar_dados() → DESCRIPTOGRAFA → Dashboard (visualização normal)
```

**Arquivo responsável:**
- `src/Components/Sidebar.py` - Função `carregar_dados()`

**Resultado no frontend:**
```python
# Usuário vê:
Responsável: João Silva

# No banco está:
Responsável: gAAAAABpIam0MiDtfUGVWT7OQZciNeaHMZmGiwc1s19hbw...
```

---

## 📂 Campos de Dados

### **Campos CRIPTOGRAFADOS** (sensíveis)
- ✅ `responsavel` - Nome do responsável

### **Campos NÃO CRIPTOGRAFADOS** (públicos)
- ❌ `nome_projeto` - Nome do projeto
- ❌ `status` - Status atual
- ❌ `data_ultima_atualizacao` - Data de atualização
- ❌ `resumo_executivo` - Resumo do projeto
- ❌ `progresso_atual` - Progresso
- ❌ `principais_desafios` - Desafios
- ❌ `acoes_corretivas` - Ações
- ❌ `perspectiva` - Perspectiva
- ❌ `resumo_ia` - Insights de IA

---

## 🛠️ Manutenção

### **Migrar Dados Existentes**

Se você adicionar dados diretamente no banco sem passar pelos leitores:

```bash
python src/Database/migrar_criptografia.py
```

Este script:
1. ✅ Detecta campos não criptografados
2. 🔐 Criptografa automaticamente
3. 💾 Atualiza o banco
4. ⏭️ Ignora dados já criptografados (seguro executar múltiplas vezes)

### **Adicionar Novo Campo Sensível**

Para criptografar um novo campo (ex: `email`):

1. **Atualizar os Leitores** (`src/Readers/leitor_*.py`):
```python
email_criptografado = encriptar_dado(linha['Email'])
```

2. **Atualizar o Carregamento** (`src/Components/Sidebar.py`):
```python
df['email'] = df['email'].apply(lambda x: decriptar_dado(x) if pd.notna(x) else x)
```

3. **Executar Migração**:
```bash
python src/Database/migrar_criptografia.py
```

---

## 🔑 Chave de Criptografia

**Localização:** `secret.key` (raiz do projeto)

⚠️ **IMPORTANTE:**
- ✅ Arquivo está no `.gitignore` (não vai para o GitHub)
- ❌ **NUNCA** compartilhe este arquivo
- 🔒 **Backup seguro** desta chave é essencial
- ⚠️ Perder a chave = perder acesso aos dados criptografados

---

## 🔒 Tecnologia

**Algoritmo:** Fernet (criptografia simétrica)
- **Biblioteca:** `cryptography` (Python)
- **Segurança:** AES-128 em modo CBC com HMAC
- **Autenticação:** Verifica integridade dos dados

---

## ✅ Checklist de Segurança

- [x] Dados sensíveis criptografados no banco
- [x] Chave de criptografia em arquivo separado
- [x] Chave no `.gitignore`
- [x] Descriptografia automática no frontend
- [x] Script de migração para dados existentes
- [x] Todos os leitores (Excel, PDF, Word) criptografam
- [ ] Sistema de autenticação de usuários (próximo passo)
- [ ] Controle de permissões por tipo de usuário (próximo passo)

---

## 📝 Próximos Passos

1. **Sistema de Login** - Autenticação de usuários
2. **Controle de Acesso** - Permissões por tipo de usuário
3. **Auditoria** - Log de acessos aos dados sensíveis
4. **Criptografia de Senha** - Hash bcrypt para senhas de usuários
