# 📊 Dashboard de Projetos MC Sonae

> Sistema completo de ETL + Business Intelligence para acompanhamento de projetos

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.51.0-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Visão Geral

Sistema de **extração, processamento e visualização** de dados de projetos que:
- 📥 Extrai dados de **Excel, PDF e Word**
- 🗄️ Armazena em **SQLite** com lógica inteligente
- 🤖 Gera **insights automáticos** com IA
- 📊 Visualiza em **dashboard interativo**

---

## ✨ Features

### 🔹 **Multi-Format ETL**
- Excel (`.xlsx`) - Dados tabulares
- PDF (`.pdf`) - Relatórios formatados  
- Word (`.docx`) - Documentos estruturados

### 🔹 **Processamento Inteligente**
- Lógica UPSERT (atualiza ou insere)
- Validação e limpeza de dados
- Geração de insights com IA (T5-small)

### 🔹 **Dashboard Completo** ⭐
- **4 Páginas Especializadas**
  - 📊 Dashboard Geral (KPIs + Gráficos)
  - 📋 Lista de Projetos (Filtros + Exportação)
  - 🔍 Detalhes Individuais (6 abas de conteúdo)
  - 🤖 Insights de IA

- **Visualizações Interativas**
  - Gráfico de Pizza (Status)
  - Timeline (Atualizações)
  - Barras (Responsáveis)

- **Recursos Avançados**
  - Filtros dinâmicos
  - Busca por projeto
  - Exportação CSV
  - Tema customizado

---

## 🚀 Quick Start

### 1️⃣ Clone e Instale

```bash
cd projeto-sonae-scraper
pip install -r requirements.txt
```

### 2️⃣ Setup Automático

```bash
bash setup.sh
```

### 3️⃣ Execute o Dashboard

```bash
streamlit run src/app_melhorado.py
```

Acesse: **http://localhost:8501** 🎉

---

## 📁 Estrutura do Projeto

```
projeto-sonae-scraper/
│
├── 📂 data/                    # Dados e banco
│   ├── relatorios_sonae.xlsx  # Fonte: Excel
│   ├── relatorio_riscos.pdf   # Fonte: PDF
│   ├── relatorio_crm.docx     # Fonte: Word
│   └── projetos_sonae.db      # Banco SQLite
│
├── 📂 src/                     # Código fonte
│   ├── leitor_excel.py        # ETL: Excel
│   ├── leitor_pdf.py          # ETL: PDF
│   ├── leitor_word.py         # ETL: Word
│   ├── processador_ia.py      # IA: Gerador de insights
│   ├── app_melhorado.py       # 🌟 Dashboard completo
│   └── app.py                 # Dashboard básico (legado)
│
├── 📂 .streamlit/
│   └── config.toml            # Tema e configurações
│
├── 📄 setup.sh                # Script de setup
├── 📄 comparar_versoes.sh     # Comparar dashboards
│
└── 📚 Documentação
    ├── GUIA_COMPLETO.md       # Guia de uso
    ├── MELHORIAS_FRONTEND.md  # Antes vs Depois
    ├── GUIA_PERSONALIZACAO.md # Como customizar
    └── RESUMO_EXECUTIVO.md    # Visão executiva
```

---

## 🛠️ Tecnologias

| Categoria | Stack |
|-----------|-------|
| **Backend** | Python 3.13, SQLite, Pandas |
| **Frontend** | Streamlit, Plotly, CSS |
| **IA** | Transformers (T5-small) |
| **ETL** | openpyxl, PyMuPDF, python-docx |

---

## 📊 Screenshots

### Dashboard Geral
![Dashboard com KPIs, gráficos de pizza e timeline]

### Detalhes do Projeto
![Página de detalhes com 6 abas de conteúdo]

### Insights de IA
![Lista de insights gerados automaticamente]

---

## 📖 Documentação

- **[GUIA_COMPLETO.md](GUIA_COMPLETO.md)** - Instruções completas de uso
- **[MELHORIAS_FRONTEND.md](MELHORIAS_FRONTEND.md)** - Comparação antes/depois
- **[GUIA_PERSONALIZACAO.md](GUIA_PERSONALIZACAO.md)** - Como customizar
- **[RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md)** - Visão executiva

---

## 🎯 Uso Manual (Passo a Passo)

```bash
# 1. Criar banco de dados
python src/cria_banco.py

# 2. Extrair dados
python src/leitor_excel.py
python src/leitor_pdf.py
python src/leitor_word.py

# 3. Gerar insights com IA (opcional)
python src/processador_ia.py

# 4. Executar dashboard
streamlit run src/app_melhorado.py
```

---

## 🆚 Comparar Versões

```bash
bash comparar_versoes.sh
```

Escolha:
1. Dashboard Básico (legado)
2. Dashboard Melhorado (recomendado)
3. Ambos lado a lado

---

## 🚀 Roadmap

### ✅ Concluído
- [x] Extração multi-formato
- [x] Banco de dados estruturado
- [x] Processamento com IA
- [x] Dashboard com 4 páginas
- [x] Gráficos interativos
- [x] Filtros e busca
- [x] Exportação CSV
- [x] Documentação completa

### 🔜 Próximos Passos
- [ ] Autenticação de usuários
- [ ] Alertas e notificações
- [ ] Exportação PDF
- [ ] API REST (FastAPI)
- [ ] Deploy em cloud
- [ ] Mobile responsivo

---

## 🤝 Contribuição

Este é um projeto acadêmico da disciplina **Projetos 2**.

---

## 👨‍💻 Autor

**Gabriel Peixoto**  
Projetos 2 - MC Sonae

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes

---

## 🎉 Agradecimentos

- Streamlit pela framework incrível
- Hugging Face pelos modelos de IA
- Comunidade Python

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
