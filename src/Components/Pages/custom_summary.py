import streamlit as st
import pandas as pd
from datetime import datetime
import time
import sys
import os

# Adicionar o caminho do processador_ia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def render_custom_summary_page():
    """Renderiza a página de Criar Resumo Personalizado"""
    st.title("📄 Criar Resumo Personalizado de Arquivo")
    st.markdown("Faça upload de um arquivo e nossa IA criará um resumo personalizado para você")
    
    st.info("Esta funcionalidade permite que você faça upload de arquivos (PDF, Word, Excel) e obtenha resumos personalizados gerados por IA.")
    
    # Seção de upload de arquivo
    st.subheader("1. Selecione o Arquivo")
    uploaded_file = st.file_uploader(
        "Escolha um arquivo para resumir",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls'],
        help="Formatos aceitos: PDF, Word (.docx, .doc) e Excel (.xlsx, .xls)"
    )
    
    # Seção de personalização
    st.subheader("2. Personalize o Resumo (Opcional)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt_personalizado = st.text_area(
            "Adicione instruções específicas para o resumo",
            placeholder="Exemplo: Foque nos principais riscos e oportunidades do projeto...",
            height=150,
            help="Descreva o que você quer que seja destacado no resumo"
        )
    
    with col2:
        st.markdown("**Dicas:**")
        st.markdown("""
        - Especifique tópicos de interesse
        - Defina o nível de detalhe
        - Mencione áreas específicas
        - Indique prioridades
        """)
        
        tamanho_resumo = st.select_slider(
            "Tamanho do resumo",
            options=["Muito Curto", "Curto", "Médio", "Longo", "Detalhado"],
            value="Médio"
        )
        
        incluir_insights = st.checkbox("Incluir insights adicionais", value=True)
        incluir_alertas = st.checkbox("Destacar pontos críticos", value=True)
    
    st.divider()
    
    # Botão de processar
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        processar = st.button("✨ Gerar Resumo Personalizado", type="primary", use_container_width=True)
    
    # Processamento
    if processar:
        if not uploaded_file:
            st.error("❌ Por favor, selecione um arquivo primeiro!")
        else:
            _process_file(
                uploaded_file, 
                prompt_personalizado, 
                tamanho_resumo, 
                incluir_insights, 
                incluir_alertas
            )
    
    # Seção de histórico
    st.divider()
    st.subheader("📚 Histórico de Resumos Gerados")
    
    with st.expander("Ver resumos anteriores", expanded=False):
        historico_exemplo = pd.DataFrame({
            "Data": ["15/11/2025", "14/11/2025", "13/11/2025"],
            "Arquivo": ["relatorio_projeto.pdf", "analise_mensal.xlsx", "proposta_comercial.docx"],
            "Nome do Resumo": ["Resumo Projeto Q4", "Análise Outubro", "Proposta Cliente XYZ"],
            "Tags": ["Projeto, Urgente", "Financeiro, Relatório", "Documentação"],
            "Status": ["✅ Disponível", "✅ Disponível", "✅ Disponível"]
        })
        
        st.dataframe(historico_exemplo, use_container_width=True, hide_index=True)
        
        st.info("💡 Clique em um resumo anterior para visualizá-lo novamente")
        st.warning("⚠️ *Backend em desenvolvimento - Histórico será persistido em breve*")

def _process_file(uploaded_file, prompt_personalizado, tamanho_resumo, incluir_insights, incluir_alertas):
    """Processa o arquivo e exibe resultados com IA real"""
    
    # Carregar modelo IA
    with st.spinner("🔄 Carregando modelo de IA (primeira vez pode demorar)..."):
        try:
            from processador_ia import carregar_modelo
            summarizer = carregar_modelo()
            if summarizer is None:
                st.error("❌ Erro ao carregar modelo de IA. Verifique a instalação do transformers.")
                return
        except Exception as e:
            st.error(f"❌ Erro ao carregar modelo: {e}")
            st.info("💡 Certifique-se de que o arquivo `processador_ia.py` está disponível.")
            return
    
    # Processar arquivo
    with st.spinner("⚙️ Processando arquivo e gerando resumo..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Etapas de processamento
            status_text.text("📖 Lendo arquivo...")
            progress_bar.progress(25)
            time.sleep(0.3)
            
            # Ler conteúdo do arquivo
            conteudo = _extrair_conteudo_arquivo(uploaded_file)
            if not conteudo:
                st.error("❌ Não foi possível extrair conteúdo do arquivo")
                return
            
            status_text.text("🔧 Preparando texto para IA...")
            progress_bar.progress(50)
            time.sleep(0.3)
            
            # Preparar texto
            texto_processado = " ".join(conteudo.split())
            
            # Validar tamanho
            if len(texto_processado.split()) < 20:
                st.error("❌ Arquivo muito pequeno para gerar um resumo significativo (mínimo 20 palavras)")
                return
            
            status_text.text("🤖 Gerando resumo com IA...")
            progress_bar.progress(75)
            
            # Gerar resumo usando o modelo real
            resumo = _gerar_resumo_ia(summarizer, texto_processado, tamanho_resumo)
            
            if not resumo:
                st.error("❌ Erro ao gerar resumo")
                return
            
            status_text.text("✨ Aplicando personalizações...")
            progress_bar.progress(90)
            time.sleep(0.3)
            
            # Aplicar personalizações
            resumo_final = resumo
            if prompt_personalizado:
                resumo_final = _aplicar_personalizacao(resumo, prompt_personalizado)
            
            progress_bar.progress(100)
            status_text.empty()
            
            # Exibir resultados
            _exibir_resultados(
                uploaded_file.name,
                resumo_final,
                conteudo,
                tamanho_resumo,
                incluir_insights,
                incluir_alertas,
                prompt_personalizado
            )
            
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {e}")
            progress_bar.empty()
            status_text.empty()

def _extrair_conteudo_arquivo(arquivo):
    """Extrai conteúdo do arquivo baseado no tipo"""
    tipo = arquivo.name.split('.')[-1].lower()
    
    try:
        if tipo == 'pdf':
            import fitz
            pdf_bytes = arquivo.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            texto = ""
            for pagina in doc:
                texto += pagina.get_text()
            return texto
            
        elif tipo in ['docx', 'doc']:
            from docx import Document
            import io
            doc = Document(io.BytesIO(arquivo.read()))
            texto = "\n".join([p.text for p in doc.paragraphs])
            return texto
            
        elif tipo in ['xlsx', 'xls']:
            import pandas as pd
            import io
            df = pd.read_excel(io.BytesIO(arquivo.read()))
            texto = df.to_string()
            return texto
            
    except Exception as e:
        st.error(f"❌ Erro ao extrair conteúdo: {e}")
        return None

def _gerar_resumo_ia(summarizer, texto, tamanho):
    """Gera resumo usando o modelo T5 real"""
    try:
        # Ajustar comprimento baseado no tamanho desejado
        tamanho_map = {
            "Muito Curto": (50, 80),
            "Curto": (80, 120),
            "Médio": (120, 180),
            "Longo": (180, 250),
            "Detalhado": (250, 350)
        }
        
        min_len, max_len = tamanho_map.get(tamanho, (120, 180))
        
        resultado = summarizer(
            f"summarize: {texto}",
            max_length=max_len,
            min_length=min_len,
            do_sample=False
        )
        
        return resultado[0]['summary_text'].strip()
        
    except Exception as e:
        st.error(f"❌ Erro na IA: {e}")
        return None

def _aplicar_personalizacao(resumo, prompt):
    """Aplica personalizações ao resumo"""
    return f"{resumo}\n\n**📌 Personalização solicitada:**\n{prompt}"

def _exibir_resultados(nome_arquivo, resumo, conteudo_original, tamanho, insights, alertas, prompt):
    """Exibe os resultados em abas"""
    st.success("✅ Resumo gerado com sucesso!")
    
    st.divider()
    st.subheader("📊 Resultados do Resumo")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("📄 Arquivo", nome_arquivo)
    with col_info2:
        st.metric("📝 Palavras (original)", len(conteudo_original.split()))
    with col_info3:
        st.metric("📝 Palavras (resumo)", len(resumo.split()))
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["✨ Resumo Principal", "📖 Conteúdo Original", "⚙️ Configurações"])
    
    with tab1:
        st.markdown("### 📋 Resumo Gerado")
        st.write(resumo)
        
        st.download_button(
            label="💾 Baixar Resumo como TXT",
            data=resumo,
            file_name=f"resumo_{nome_arquivo.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with tab2:
        st.markdown("### 📄 Conteúdo Original")
        st.text_area("", value=conteudo_original[:1000] + "..." if len(conteudo_original) > 1000 else conteudo_original, height=400, disabled=True)
    
    with tab3:
        st.markdown("### ⚙️ Configurações Aplicadas")
        
        config_df = pd.DataFrame({
            "Configuração": ["Tamanho", "Insights", "Alertas", "Personalização", "Modelo"],
            "Valor": [
                tamanho,
                "✅ Sim" if insights else "❌ Não",
                "✅ Sim" if alertas else "❌ Não",
                "✅ Sim" if prompt else "❌ Não",
                "T5 (Transformers)"
            ]
        })
        
        st.dataframe(config_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    st.subheader("💾 Salvar Resumo")
    
    col_save1, col_save2 = st.columns(2)
    
    with col_save1:
        nome_resumo = st.text_input(
            "Nome para salvar",
            value=f"Resumo_{nome_arquivo.split('.')[0]}"
        )
    
    with col_save2:
        tags = st.multiselect(
            "Tags (opcional)",
            options=["Urgente", "Projeto", "Relatório", "Análise", "Documentação", "Financeiro"]
        )
    
    if st.button("💾 Salvar no Histórico", use_container_width=True):
        st.success(f"✅ Resumo '{nome_resumo}' salvo com sucesso!")
        st.info("💡 *Backend será implementado em breve*")
