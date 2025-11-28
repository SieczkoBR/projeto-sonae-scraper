#!/bin/bash

# Script de Setup Completo do Projeto MC Sonae
# Execute com: bash setup.sh

echo "🚀 Iniciando Setup do Dashboard MC Sonae..."
echo ""

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Execute este script da raiz do projeto"
    exit 1
fi

# 1. Criar banco de dados
echo "📊 1/5 - Criando estrutura do banco de dados..."
python src/Database/cria_banco.py
if [ $? -eq 0 ]; then
    echo "✅ Banco criado com sucesso"
else
    echo "❌ Erro ao criar banco"
    exit 1
fi

echo ""

# 2. Extrair dados do Excel
echo "📗 2/5 - Extraindo dados do Excel..."
if [ -f "data/relatorios_sonae.xlsx" ]; then
    python src/Readers/leitor_excel.py
    echo "✅ Dados do Excel processados"
else
    echo "⚠️  Arquivo Excel não encontrado - pulando"
fi

echo ""

# 3. Extrair dados do PDF
echo "📕 3/5 - Extraindo dados do PDF..."
if [ -f "data/relatorio_riscos.pdf" ]; then
    python src/Readers/leitor_pdf.py
    echo "✅ Dados do PDF processados"
else
    echo "⚠️  Arquivo PDF não encontrado - pulando"
fi

echo ""

# 4. Extrair dados do Word
echo "📘 4/5 - Extraindo dados do Word..."
if [ -f "data/relatorio_crm.docx" ]; then
    python src/Readers/leitor_word.py
    echo "✅ Dados do Word processados"
else
    echo "⚠️  Arquivo Word não encontrado - pulando"
fi

echo ""

# 5. Gerar insights com IA (opcional)
echo "🤖 5/5 - Gerando insights com IA..."
read -p "Deseja gerar insights com IA? (pode demorar) [s/N]: " gerar_ia

if [[ $gerar_ia =~ ^[Ss]$ ]]; then
    echo "⌛ Processando com IA (isso pode demorar na primeira vez)..."
    python src/AI/processador_ia.py
    echo "✅ Insights gerados"
else
    echo "⏭️  Pulando geração de IA"
fi

echo ""
echo "🎉 Setup concluído com sucesso!"
echo ""
echo "Para iniciar o dashboard, execute:"
echo "  streamlit run src/App.py"
echo ""
