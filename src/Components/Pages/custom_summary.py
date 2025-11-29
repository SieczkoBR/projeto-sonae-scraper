import streamlit as st
import pandas as pd
from datetime import datetime
import time
import sys
import os

# Adicionar o caminho do processador_ia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Importar o gerenciador de relatórios
from Database.relatorios_db import RelatoriosDB

def render_custom_summary_page():
    """Renderiza a página de Criar Relatório Executivo Automático"""
    st.title("📊 Gerador de Relatório Executivo com IA")
    st.markdown("Envie um arquivo e nossa IA criará um **relatório executivo completo** com análise estratégica, insights e recomendações")
    
    st.info("💡 A IA analisa profundamente o conteúdo e gera um relatório profissional com visão executiva, identificando objetivos, riscos, oportunidades e ações recomendadas.")
    
    # Inicializar session_state para persistir o relatório
    if 'relatorio_atual' not in st.session_state:
        st.session_state.relatorio_atual = None
    
    # Seção de upload de arquivo
    st.subheader("1. Selecione o Arquivo")
    uploaded_file = st.file_uploader(
        "Escolha um arquivo para análise",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls'],
        help="Formatos aceitos: PDF, Word (.docx, .doc) e Excel (.xlsx, .xls)"
    )
    
    # Seção de personalização
    st.subheader("2. Personalize a Análise (Opcional)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt_personalizado = st.text_area(
            "Instruções específicas para o relatório",
            placeholder="Exemplo: Foque em análise de riscos financeiros e oportunidades de mercado...",
            height=150,
            help="Descreva aspectos específicos que você quer que a IA analise"
        )
    
    with col2:
        st.markdown("**Dicas:**")
        st.markdown("""
        - Indique área de foco
        - Mencione stakeholders
        - Defina prioridades
        - Especifique contexto
        """)
        
        tamanho_resumo = st.select_slider(
            "Nível de detalhe",
            options=["Muito Curto", "Curto", "Médio", "Longo", "Detalhado"],
            value="Médio",
            help="Quanto mais detalhado, mais insights e análises a IA fornecerá"
        )
        
        incluir_insights = st.checkbox("Incluir insights estratégicos", value=True)
        incluir_alertas = st.checkbox("Destacar pontos críticos e riscos", value=True)
        # Gráficos removidos
        incluir_graficos = False
    
    st.divider()
    
    # Botão de processar
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        processar = st.button("🤖 Gerar Relatório Executivo", type="primary", use_container_width=True)
    
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
                incluir_alertas,
                incluir_graficos
            )
    
    # Exibir relatório se existe um no session_state
    if st.session_state.relatorio_atual is not None:
        _exibir_resultados(
            st.session_state.relatorio_atual['nome_arquivo'],
            st.session_state.relatorio_atual['relatorio'],
            st.session_state.relatorio_atual['conteudo_original'],
            st.session_state.relatorio_atual['tamanho'],
            st.session_state.relatorio_atual['insights'],
            st.session_state.relatorio_atual['alertas'],
            st.session_state.relatorio_atual['prompt'],
            st.session_state.relatorio_atual.get('dados_graficos')
        )
    
    # Seção de histórico
    st.divider()
    st.subheader("📚 Histórico de Relatórios Gerados")
    
    with st.expander("Ver relatórios anteriores", expanded=False):
        # Buscar relatórios do banco de dados
        db = RelatoriosDB()
        relatorios = db.listar_relatorios(limite=20)
        
        if relatorios:
            # Preparar dados para exibição
            dados_tabela = []
            for rel in relatorios:
                dados_tabela.append({
                    "Data": rel['data_criacao'].split()[0] if rel['data_criacao'] else "",
                    "Arquivo": rel['arquivo_original'] if rel['arquivo_original'] else "N/A",
                    "Nome do Relatório": rel['nome_relatorio'],
                    "Tags": rel['tags'] if rel['tags'] else "",
                    "Status": "✅ Disponível"
                })
            
            df_historico = pd.DataFrame(dados_tabela)
            st.dataframe(df_historico, use_container_width=True, hide_index=True)
            
            # Seletor para visualizar relatório
            st.markdown("---")
            relatorio_selecionado = st.selectbox(
                "Selecione um relatório para visualizar",
                options=["Selecione..."] + [f"{rel['id']} - {rel['nome_relatorio']}" for rel in relatorios]
            )
            
            if relatorio_selecionado != "Selecione...":
                rel_id = int(relatorio_selecionado.split(" - ")[0])
                relatorio_completo = db.buscar_relatorio_por_id(rel_id)
                
                if relatorio_completo:
                    st.markdown("---")
                    st.markdown(f"### 📄 {relatorio_completo['nome_relatorio']}")
                    st.caption(f"📅 Criado em: {relatorio_completo['data_criacao']}")
                    
                    if relatorio_completo['tags']:
                        st.caption(f"🏷️ Tags: {relatorio_completo['tags']}")
                    
                    st.markdown("---")
                    st.markdown(relatorio_completo['conteudo_relatorio'])
                    
                    # Botão para deletar
                    col_del1, col_del2, col_del3 = st.columns([1, 1, 1])
                    with col_del2:
                        if st.button("🗑️ Deletar este relatório", type="secondary", use_container_width=True, key=f"del_{rel_id}"):
                            if db.deletar_relatorio(rel_id):
                                st.success("✅ Relatório deletado com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao deletar relatório")
        else:
            st.info("📭 Nenhum relatório salvo ainda. Gere e salve seu primeiro relatório!")

def _process_file(uploaded_file, prompt_personalizado, tamanho_resumo, incluir_insights, incluir_alertas, incluir_graficos=False):
    """Processa o arquivo e exibe relatório executivo com IA"""
    
    # Carregar modelo IA
    with st.spinner("🔄 Carregando modelo de IA (primeira vez pode demorar alguns minutos)..."):
        try:
            from AI.processador_ia import carregar_modelo, gerar_relatorio_executivo
            modelo = carregar_modelo()
            if modelo is None:
                st.error("❌ Erro ao carregar modelo de IA.")
                return
        except Exception as e:
            st.error(f"❌ Erro ao carregar modelo: {e}")
            import traceback
            st.code(traceback.format_exc())
            return
    
    # Processar arquivo
    with st.spinner("⚙️ Analisando arquivo e gerando relatório executivo..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Etapas de processamento
            status_text.text("📖 Extraindo conteúdo do arquivo...")
            progress_bar.progress(20)
            time.sleep(0.3)
            
            # Ler conteúdo do arquivo
            conteudo = _extrair_conteudo_arquivo(uploaded_file)
            if not conteudo:
                st.error("❌ Não foi possível extrair conteúdo do arquivo")
                return
            
            status_text.text("🧠 Analisando conteúdo com IA...")
            progress_bar.progress(40)
            time.sleep(0.3)
            
            # Validar tamanho
            if len(conteudo.strip()) < 50:
                st.error("❌ Arquivo muito pequeno para análise executiva (mínimo 50 caracteres)")
                return
            
            status_text.text("📊 Gerando relatório executivo...")
            progress_bar.progress(60)
            
            # Gerar relatório usando FLAN-T5
            resultado = gerar_relatorio_executivo(
                modelo, 
                conteudo, 
                tamanho_resumo,
                prompt_personalizado,
                incluir_graficos
            )
            
            if not resultado or not resultado.get("texto"):
                st.error("❌ Erro ao gerar relatório")
                return
            
            status_text.text("✨ Finalizando formatação...")
            progress_bar.progress(90)
            time.sleep(0.3)
            
            progress_bar.progress(100)
            status_text.empty()
            
            # Salvar no session_state para persistir
            st.session_state.relatorio_atual = {
                'nome_arquivo': uploaded_file.name,
                'relatorio': resultado["texto"],
                'conteudo_original': conteudo,
                'tamanho': tamanho_resumo,
                'insights': incluir_insights,
                'alertas': incluir_alertas,
                'prompt': prompt_personalizado,
                'dados_graficos': resultado.get("dados_graficos")
            }
            
            # Recarregar para mostrar o relatório
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {e}")
            import traceback
            st.code(traceback.format_exc())
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

def _exibir_resultados(nome_arquivo, relatorio, conteudo_original, tamanho, insights, alertas, prompt, dados_graficos=None):
    """Exibe os resultados do relatório executivo"""
    st.success("✅ Relatório executivo gerado com sucesso!")
    
    st.divider()
    
    # CSS customizado para melhor formatação
    st.markdown("""
    <style>
    .relatorio-container {
        font-size: 1.15rem;
        line-height: 1.9;
        font-weight: 400;
    }
    .relatorio-container h2 {
        font-size: 1.9rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #1f77b4;
        font-weight: 600;
    }
    .relatorio-container h3 {
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        color: #2ca02c;
        font-weight: 600;
    }
    .relatorio-container p {
        margin-bottom: 1.2rem;
        font-weight: 400;
    }
    .relatorio-container ul, .relatorio-container ol {
        margin-bottom: 1.2rem;
        padding-left: 2rem;
    }
    .relatorio-container li {
        margin-bottom: 0.6rem;
        font-weight: 400;
    }
    .relatorio-container strong {
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.info(f"📄 **Arquivo analisado:** {nome_arquivo}")
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📊 Relatório Executivo", "📖 Documento Original", "⚙️ Configurações"])
    
    with tab1:
        st.markdown('<div class="relatorio-container">', unsafe_allow_html=True)
        st.markdown(relatorio)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráficos removidos
        if False and dados_graficos:
            st.divider()
            st.markdown("## 📈 Visualizações de Dados")
            
            import plotly.graph_objects as go
            
            for nome_grafico, config in dados_graficos.items():
                # Mostrar título e descrição do gráfico
                st.markdown(f"### {config['titulo']}")
                if 'descricao' in config:
                    st.info(config['descricao'])
                
                # Criar legenda textual com os itens
                st.markdown("**Métricas analisadas:**")
                for i, (label, valor) in enumerate(zip(config['labels'], config['valores']), 1):
                    if 'progresso' in nome_grafico:
                        st.markdown(f"• **{label}**: {valor}%")
                    else:
                        st.markdown(f"• **{label}**: R$ {valor:,.2f}")
                
                st.markdown("")  # Espaçamento
                
                if config['tipo'] == 'barra':
                    # Criar labels abreviados para o gráfico
                    labels_curtos = [f"Item {i+1}" for i in range(len(config['labels']))]
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=labels_curtos, 
                            y=config['valores'], 
                            marker_color='#1f77b4',
                            text=config['valores'],
                            texttemplate='%{text}%' if 'progresso' in nome_grafico else 'R$ %{text:,.0f}',
                            textposition='outside',
                            hovertemplate='<b>%{fullData.customdata[%{pointIndex}]}</b><br>Valor: %{y}%<extra></extra>' if 'progresso' in nome_grafico else '<b>%{fullData.customdata[%{pointIndex}]}</b><br>Valor: R$ %{y:,.2f}<extra></extra>',
                            customdata=config['labels']
                        )
                    ])
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Percentual (%)" if 'progresso' in nome_grafico else "Valor (R$)",
                        showlegend=False,
                        height=500,
                        margin=dict(b=80, t=40, l=60, r=40),
                        xaxis=dict(
                            tickangle=0,
                            tickfont=dict(size=12)
                        ),
                        yaxis=dict(
                            tickfont=dict(size=12),
                            gridcolor='rgba(128,128,128,0.2)'
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif config['tipo'] == 'linha':
                    labels_curtos = [f"Item {i+1}" for i in range(len(config['labels']))]
                    
                    fig = go.Figure(data=[
                        go.Scatter(
                            x=labels_curtos, 
                            y=config['valores'],
                            mode='lines+markers',
                            line=dict(color='#2ca02c', width=3),
                            marker=dict(size=10),
                            hovertemplate='<b>%{fullData.customdata[%{pointIndex}]}</b><br>Valor: R$ %{y:,.2f}<extra></extra>',
                            customdata=config['labels']
                        )
                    ])
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Valor (R$)",
                        showlegend=False,
                        height=500,
                        margin=dict(b=80, t=40, l=60, r=40),
                        xaxis=dict(
                            tickangle=0,
                            tickfont=dict(size=12)
                        ),
                        yaxis=dict(
                            tickfont=dict(size=12),
                            gridcolor='rgba(128,128,128,0.2)'
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")  # Separador entre gráficos
        
        st.divider()
        
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            st.download_button(
                label="💾 Baixar Relatório (TXT)",
                data=relatorio,
                file_name=f"relatorio_executivo_{nome_arquivo.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_download2:
            st.download_button(
                label="📄 Baixar Relatório (MD)",
                data=relatorio,
                file_name=f"relatorio_executivo_{nome_arquivo.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    with tab2:
        st.markdown("### 📄 Conteúdo Original do Documento")
        preview = conteudo_original[:2000] + "..." if len(conteudo_original) > 2000 else conteudo_original
        st.text_area("Prévia do documento", value=preview, height=400, disabled=True, label_visibility="collapsed")
        st.caption(f"Mostrando primeiros 2000 caracteres de {len(conteudo_original)} totais")
    
    with tab3:
        st.markdown("### ⚙️ Configurações Aplicadas")
        
        config_df = pd.DataFrame({
            "Configuração": ["Nível de Detalhe", "Insights Estratégicos", "Alertas e Riscos", "Personalização", "Modelo IA"],
            "Valor": [
                tamanho,
                "✅ Sim" if insights else "❌ Não",
                "✅ Sim" if alertas else "❌ Não",
                "✅ Sim" if prompt else "❌ Não",
                "FLAN-T5 Base"
            ]
        })
        
        st.dataframe(config_df, use_container_width=True, hide_index=True)
        
        if prompt:
            st.markdown("**Instruções personalizadas fornecidas:**")
            st.info(prompt)
    
    st.divider()
    
    st.subheader("💾 Salvar Relatório")
    
    col_save1, col_save2 = st.columns(2)
    
    with col_save1:
        nome_relatorio = st.text_input(
            "Nome para salvar",
            value=f"Relatorio_{nome_arquivo.split('.')[0]}",
            key=f"nome_save_{id(nome_arquivo)}"
        )
    
    with col_save2:
        tags = st.multiselect(
            "Tags (opcional)",
            options=["Urgente", "Projeto", "Relatório", "Análise", "Documentação", "Financeiro", "Estratégico"],
            key=f"tags_save_{id(nome_arquivo)}"
        )
    
    col_btn_save, col_btn_clear = st.columns(2)
    
    with col_btn_save:
        if st.button("💾 Salvar no Histórico", use_container_width=True, type="primary", key=f"btn_salvar_{id(nome_arquivo)}"):
            if nome_relatorio.strip():
                db = RelatoriosDB()
                sucesso = db.salvar_relatorio(
                    nome_relatorio=nome_relatorio,
                    conteudo_relatorio=relatorio,
                    arquivo_original=nome_arquivo,
                    tags=tags,
                    tamanho_detalhe=tamanho,
                    prompt_personalizado=prompt if prompt else None,
                    user_id=None  # Por enquanto None, depois será o ID do usuário logado
                )
                
                if sucesso:
                    st.success(f"✅ Relatório '{nome_relatorio}' salvo com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Erro ao salvar relatório no banco de dados")
            else:
                st.warning("⚠️ Por favor, forneça um nome para o relatório")
    
    with col_btn_clear:
        if st.button("🗑️ Novo Relatório", use_container_width=True, type="secondary", key=f"btn_clear_{id(nome_arquivo)}"):
            st.session_state.relatorio_atual = None
            st.rerun()
