import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard MC Sonae",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Customizado para Melhorar o Visual ---
st.markdown("""
    <style>
    /* Estilo para cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2.5em;
        font-weight: bold;
    }
    
    .metric-card p {
        margin: 5px 0 0 0;
        font-size: 1.1em;
        opacity: 0.9;
    }
    
    /* Estilo para status badges */
    .status-badge {
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    
    .status-concluido {
        background-color: #10b981;
        color: white;
    }
    
    .status-andamento {
        background-color: #f59e0b;
        color: white;
    }
    
    .status-atrasado {
        background-color: #ef4444;
        color: white;
    }
    
    /* Melhorias gerais */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Sidebar personalizada */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    }
    
    /* Texto da sidebar em branco */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {
        color: white !important;
    }
    
    /* Campos de input com fundo branco e texto escuro */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] input {
        background-color: white !important;
        color: #262730 !important;
    }
    
    /* Botão na sidebar */
    [data-testid="stSidebar"] button {
        background-color: white !important;
        color: #1e3a8a !important;
        border: 2px solid white !important;
        font-weight: bold !important;
    }
    
    [data-testid="stSidebar"] button p,
    [data-testid="stSidebar"] button div,
    [data-testid="stSidebar"] button span {
        color: #1e3a8a !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #f0f2f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Constantes ---
CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")

# --- Funções Auxiliares ---
@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_dados():
    """Carrega dados do banco SQLite"""
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        df = pd.read_sql_query("SELECT * FROM projetos", conexao)
        conexao.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

def get_status_info(status):
    """Retorna ícone, cor e texto do status"""
    status_lower = str(status).lower()
    
    if "atrasado" in status_lower or "crítico" in status_lower:
        return "🔴", "#ef4444", "Atrasado"
    elif "concluído" in status_lower or "concluido" in status_lower:
        return "🟢", "#10b981", "Concluído"
    elif "em andamento" in status_lower or "andamento" in status_lower:
        return "🟡", "#f59e0b", "Em Andamento"
    elif "no prazo" in status_lower:
        return "🔵", "#3b82f6", "No Prazo"
    else:
        return "⚪️", "#6b7280", str(status)

def criar_grafico_status(df):
    """Cria gráfico de pizza para distribuição de status"""
    if df.empty:
        return None
    
    # Normaliza os status
    df_viz = df.copy()
    df_viz['status_normalizado'] = df_viz['status'].apply(lambda x: get_status_info(x)[2])
    
    status_counts = df_viz['status_normalizado'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Distribuição de Status dos Projetos",
        color_discrete_map={
            "Concluído": "#10b981",
            "Em Andamento": "#f59e0b",
            "Atrasado": "#ef4444",
            "No Prazo": "#3b82f6"
        },
        hole=0.4  # Donut chart
    )
    
    fig.update_layout(
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_timeline_projetos(df):
    """Cria linha do tempo dos projetos"""
    if df.empty or 'data_ultima_atualizacao' not in df.columns:
        return None
    
    df_timeline = df.copy()
    df_timeline['data_ultima_atualizacao'] = pd.to_datetime(
        df_timeline['data_ultima_atualizacao'], 
        errors='coerce'
    )
    
    df_timeline = df_timeline.dropna(subset=['data_ultima_atualizacao'])
    df_timeline = df_timeline.sort_values('data_ultima_atualizacao')
    
    if df_timeline.empty:
        return None
    
    fig = px.scatter(
        df_timeline,
        x='data_ultima_atualizacao',
        y='nome_projeto',
        color='status',
        title="Linha do Tempo das Atualizações",
        labels={'data_ultima_atualizacao': 'Data', 'nome_projeto': 'Projeto'},
        height=400
    )
    
    fig.update_traces(marker=dict(size=12))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    )
    
    return fig

# --- SIDEBAR: Filtros e Navegação ---
with st.sidebar:
    st.title("🎯 Navegação")
    
    pagina = st.radio(
        "Escolha uma página:",
        ["📊 Dashboard Geral", "📋 Lista de Projetos", "🔍 Detalhes do Projeto", "🤖 Insights de IA", "📄 Criar Resumo Personalizado"]
    )
    
    st.divider()
    
    st.subheader("🔍 Filtros")
    
    # Carrega dados para os filtros
    df_projetos = carregar_dados()
    
    if not df_projetos.empty:
        # Filtro por status
        status_unicos = ["Todos"] + sorted(df_projetos['status'].dropna().unique().tolist())
        filtro_status = st.selectbox("Status:", status_unicos)
        
        # Filtro por responsável
        responsaveis = ["Todos"] + sorted(df_projetos['responsavel'].dropna().unique().tolist())
        filtro_responsavel = st.selectbox("Responsável:", responsaveis)
        
        # Aplicar filtros
        df_filtrado = df_projetos.copy()
        
        if filtro_status != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
        
        if filtro_responsavel != "Todos":
            df_filtrado = df_filtrado[df_filtrado['responsavel'] == filtro_responsavel]
    else:
        df_filtrado = df_projetos
        st.warning("Sem dados para filtrar")
    
    st.divider()
    
    # Botão para atualizar dados
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- PÁGINA 1: DASHBOARD GERAL ---
if pagina == "📊 Dashboard Geral":
    st.title("📊 Dashboard Geral de Projetos MC Sonae")
    st.markdown("Visão completa do portfólio de projetos")
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado. Execute os scripts de extração primeiro.")
    else:
        # --- KPIs no topo ---
        col1, col2, col3, col4 = st.columns(4)
        
        total_projetos = len(df_filtrado)
        concluidos = len(df_filtrado[df_filtrado['status'].str.contains('concluído|concluido', case=False, na=False)])
        em_andamento = len(df_filtrado[df_filtrado['status'].str.contains('andamento', case=False, na=False)])
        atrasados = len(df_filtrado[df_filtrado['status'].str.contains('atrasado|crítico', case=False, na=False)])
        
        with col1:
            st.metric("Total de Projetos", total_projetos, delta=None)
        
        with col2:
            st.metric("Concluídos", concluidos, delta=f"{(concluidos/total_projetos*100):.0f}%" if total_projetos > 0 else "0%")
        
        with col3:
            st.metric("Em Andamento", em_andamento, delta=None)
        
        with col4:
            st.metric("Atrasados", atrasados, delta=f"-{atrasados}" if atrasados > 0 else "0", delta_color="inverse")
        
        st.divider()
        
        # --- Gráficos ---
        col_esq, col_dir = st.columns(2)
        
        with col_esq:
            fig_status = criar_grafico_status(df_filtrado)
            if fig_status:
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col_dir:
            fig_timeline = criar_timeline_projetos(df_filtrado)
            if fig_timeline:
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.info("📅 Sem dados de timeline disponíveis")
        
        st.divider()
        
        # --- Projetos por Responsável ---
        st.subheader("👥 Projetos por Responsável")
        
        if 'responsavel' in df_filtrado.columns:
            responsavel_counts = df_filtrado['responsavel'].value_counts().head(10)
            
            fig_resp = px.bar(
                x=responsavel_counts.values,
                y=responsavel_counts.index,
                orientation='h',
                title="Top 10 Responsáveis",
                labels={'x': 'Número de Projetos', 'y': 'Responsável'},
                color=responsavel_counts.values,
                color_continuous_scale='Blues'
            )
            
            fig_resp.update_layout(
                showlegend=False,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_resp, use_container_width=True)

# --- PÁGINA 2: LISTA DE PROJETOS ---
elif pagina == "📋 Lista de Projetos":
    st.title("📋 Lista Completa de Projetos")
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum projeto encontrado")
    else:
        st.info(f"📊 Mostrando {len(df_filtrado)} projeto(s)")
        
        # Criar coluna de status visual
        df_display = df_filtrado.copy()
        df_display['Status Visual'] = df_display['status'].apply(lambda x: get_status_info(x)[0] + " " + get_status_info(x)[2])
        
        # Configuração das colunas
        colunas_exibir = ['nome_projeto', 'Status Visual', 'responsavel', 'data_ultima_atualizacao']
        colunas_disponiveis = [col for col in colunas_exibir if col in df_display.columns]
        
        config_colunas = {
            "nome_projeto": st.column_config.TextColumn("📁 Projeto", width="large"),
            "Status Visual": st.column_config.TextColumn("🎯 Status", width="medium"),
            "responsavel": st.column_config.TextColumn("👤 Responsável", width="medium"),
            "data_ultima_atualizacao": st.column_config.TextColumn("📅 Última Atualização", width="medium")
        }
        
        st.dataframe(
            df_display[colunas_disponiveis],
            column_config=config_colunas,
            hide_index=True,
            use_container_width=True,
            height=600
        )
        
        # Botão para baixar dados
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar dados como CSV",
            data=csv,
            file_name=f"projetos_sonae_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# --- PÁGINA 3: DETALHES DO PROJETO ---
elif pagina == "🔍 Detalhes do Projeto":
    st.title("🔍 Detalhes Completos do Projeto")
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum projeto disponível")
    else:
        # Seletor de projeto
        projeto_selecionado = st.selectbox(
            "Selecione um projeto:",
            df_filtrado['nome_projeto'].tolist(),
            index=0
        )
        
        # Filtrar dados do projeto
        projeto = df_filtrado[df_filtrado['nome_projeto'] == projeto_selecionado].iloc[0]
        
        # Header com status
        col_nome, col_status = st.columns([3, 1])
        
        with col_nome:
            st.header(projeto['nome_projeto'])
        
        with col_status:
            icone, cor, texto = get_status_info(projeto['status'])
            st.markdown(f"### {icone} {texto}")
        
        st.divider()
        
        # Informações básicas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👤 Responsável", projeto.get('responsavel', 'N/A'))
        
        with col2:
            st.metric("📅 Última Atualização", projeto.get('data_ultima_atualizacao', 'N/A'))
        
        with col3:
            st.metric("📂 Fonte", projeto.get('fonte_dados', 'N/A').split('/')[-1])
        
        st.divider()
        
        # Abas para conteúdo detalhado
        tabs = st.tabs(["📝 Resumo Executivo", "📈 Progresso", "⚠️ Desafios", "🔧 Ações", "🔮 Perspectiva", "🤖 Insight IA"])
        
        with tabs[0]:
            if projeto.get('resumo_executivo'):
                st.markdown(projeto['resumo_executivo'])
            else:
                st.info("Sem resumo executivo disponível")
        
        with tabs[1]:
            if projeto.get('progresso_atual'):
                st.markdown(projeto['progresso_atual'])
            else:
                st.info("Sem informações de progresso disponíveis")
        
        with tabs[2]:
            if projeto.get('principais_desafios'):
                st.markdown(projeto['principais_desafios'])
            else:
                st.info("Sem desafios registrados")
        
        with tabs[3]:
            if projeto.get('acoes_corretivas'):
                st.markdown(projeto['acoes_corretivas'])
            else:
                st.info("Sem ações corretivas registradas")
        
        with tabs[4]:
            if projeto.get('perspectiva'):
                st.markdown(projeto['perspectiva'])
            else:
                st.info("Sem perspectiva disponível")
        
        with tabs[5]:
            if projeto.get('resumo_ia'):
                st.success(f"🤖 **Insight Automático:** {projeto['resumo_ia']}")
            else:
                st.warning("🤖 Insight de IA ainda não gerado. Execute `processador_ia.py`")

# --- PÁGINA 4: INSIGHTS DE IA ---
elif pagina == "🤖 Insights de IA":
    st.title("🤖 Insights Gerados por IA")
    st.markdown("Resumos automáticos gerados pelo modelo T5")
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum projeto disponível")
    else:
        # Filtrar apenas projetos com IA
        df_com_ia = df_filtrado[df_filtrado['resumo_ia'].notna()]
        
        if df_com_ia.empty:
            st.info("🤖 Nenhum insight de IA foi gerado ainda. Execute `python src/processador_ia.py`")
        else:
            st.success(f"✅ {len(df_com_ia)} projeto(s) com insights de IA")
            
            for idx, projeto in df_com_ia.iterrows():
                with st.expander(f"🔍 {projeto['nome_projeto']}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**🤖 Insight Automático:**")
                        st.info(projeto['resumo_ia'])
                    
                    with col2:
                        icone, cor, texto = get_status_info(projeto['status'])
                        st.markdown(f"**Status:** {icone} {texto}")
                        st.markdown(f"**Responsável:** {projeto.get('responsavel', 'N/A')}")

# --- PÁGINA 5: CRIAR RESUMO PERSONALIZADO ---
elif pagina == "📄 Criar Resumo Personalizado":
    st.title("📄 Criar Resumo Personalizado de Arquivo")
    st.markdown("Faça upload de um arquivo e nossa IA criará um resumo personalizado para você")
    
    # Container principal
    st.info("ℹ️ Esta funcionalidade permite que você faça upload de arquivos (PDF, Word, Excel) e obtenha resumos personalizados gerados por IA.")
    
    # Seção de upload de arquivo
    st.subheader("📤 1. Selecione o Arquivo")
    uploaded_file = st.file_uploader(
        "Escolha um arquivo para resumir",
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls'],
        help="Formatos aceitos: PDF, Word (.docx, .doc) e Excel (.xlsx, .xls)"
    )
    
    # Seção de personalização
    st.subheader("✨ 2. Personalize o Resumo (Opcional)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt_personalizado = st.text_area(
            "Adicione instruções específicas para o resumo",
            placeholder="Exemplo: Foque nos principais riscos e oportunidades do projeto, destacando prazos críticos...",
            height=150,
            help="Descreva o que você quer que seja destacado no resumo"
        )
    
    with col2:
        st.markdown("**💡 Dicas de personalização:**")
        st.markdown("""
        - Especifique tópicos de interesse
        - Defina o nível de detalhe
        - Mencione áreas específicas
        - Indique prioridades
        """)
        
        # Opções adicionais
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
        processar = st.button("🚀 Gerar Resumo Personalizado", type="primary", use_container_width=True)
    
    # Processamento (frontend mockup)
    if processar:
        if not uploaded_file:
            st.error("❌ Por favor, selecione um arquivo primeiro!")
        else:
            # Simulação de processamento
            with st.spinner("🔄 Processando arquivo e gerando resumo..."):
                import time
                
                # Barra de progresso com etapas
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Etapa 1: Upload
                status_text.text("📤 Fazendo upload do arquivo...")
                time.sleep(0.5)
                progress_bar.progress(20)
                
                # Etapa 2: Leitura
                status_text.text("📖 Lendo e extraindo conteúdo do arquivo...")
                time.sleep(0.8)
                progress_bar.progress(40)
                
                # Etapa 3: Processamento
                status_text.text("🤖 Processando com IA...")
                time.sleep(1)
                progress_bar.progress(70)
                
                # Etapa 4: Aplicando personalização
                if prompt_personalizado:
                    status_text.text("✨ Aplicando suas personalizações...")
                    time.sleep(0.5)
                progress_bar.progress(90)
                
                # Etapa 5: Finalização
                status_text.text("✅ Finalizando...")
                time.sleep(0.3)
                progress_bar.progress(100)
                status_text.empty()
            
            st.success("✅ Resumo gerado com sucesso!")
            
            # Exibir resultados (mockup)
            st.divider()
            st.subheader("📊 Resultados do Resumo")
            
            # Informações do arquivo
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("📁 Arquivo", uploaded_file.name)
            with col_info2:
                st.metric("📏 Tamanho", f"{uploaded_file.size / 1024:.1f} KB")
            with col_info3:
                st.metric("📅 Processado em", datetime.now().strftime("%d/%m/%Y %H:%M"))
            
            st.divider()
            
            # Tabs para diferentes visualizações
            tab1, tab2, tab3 = st.tabs(["📝 Resumo Principal", "🔍 Detalhes Extraídos", "⚙️ Configurações Aplicadas"])
            
            with tab1:
                st.markdown("### 📝 Resumo Gerado")
                
                # Resumo mockup baseado no tipo de arquivo
                resumo_exemplo = f"""
                **Resumo Automático do Arquivo: {uploaded_file.name}**
                
                Este documento foi processado e analisado pela nossa IA. Aqui está um resumo {tamanho_resumo.lower()} 
                do conteúdo identificado:
                
                **Principais Pontos Identificados:**
                - Análise estrutural do documento realizada com sucesso
                - Conteúdo organizado e categorizado
                - Informações relevantes extraídas e processadas
                
                **Contexto e Relevância:**
                O arquivo contém informações que foram categorizadas e estruturadas para facilitar a compreensão.
                A análise identificou seções principais, dados relevantes e estrutura do documento.
                """
                
                if prompt_personalizado:
                    resumo_exemplo += f"""
                
                **Personalização Aplicada:**
                Seu prompt: "{prompt_personalizado}"
                
                Com base nas suas instruções específicas, o resumo foi ajustado para focar nos aspectos 
                que você mencionou, garantindo que as informações mais relevantes para seu contexto sejam destacadas.
                """
                
                if incluir_insights:
                    resumo_exemplo += """
                
                **💡 Insights Adicionais:**
                - Documento apresenta estrutura organizada
                - Conteúdo adequado para processamento automatizado
                - Formato compatível com análise de IA
                """
                
                if incluir_alertas:
                    resumo_exemplo += """
                
                **⚠️ Pontos de Atenção:**
                - Recomenda-se validação manual de informações críticas
                - Alguns dados podem requerer contexto adicional
                - Verificar datas e valores numéricos importantes
                """
                
                st.markdown(resumo_exemplo)
                
                # Botão para copiar
                st.download_button(
                    label="📥 Baixar Resumo como TXT",
                    data=resumo_exemplo,
                    file_name=f"resumo_{uploaded_file.name.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
            
            with tab2:
                st.markdown("### 🔍 Informações Detalhadas Extraídas")
                
                # Mockup de detalhes extraídos
                col_det1, col_det2 = st.columns(2)
                
                with col_det1:
                    st.markdown("**📊 Estatísticas do Documento:**")
                    st.info(f"""
                    - **Tipo:** {uploaded_file.type}
                    - **Tamanho:** {uploaded_file.size / 1024:.2f} KB
                    - **Formato:** {uploaded_file.name.split('.')[-1].upper()}
                    """)
                
                with col_det2:
                    st.markdown("**🎯 Processamento:**")
                    st.success(f"""
                    - **Status:** Concluído
                    - **Qualidade:** Alta
                    - **Confiança:** 95%
                    """)
                
                st.markdown("**📋 Estrutura Identificada:**")
                st.code("""
                Estrutura do documento:
                ├── Seção 1: Introdução
                ├── Seção 2: Conteúdo Principal
                ├── Seção 3: Dados e Informações
                └── Seção 4: Conclusões
                """, language="text")
            
            with tab3:
                st.markdown("### ⚙️ Configurações Aplicadas no Processamento")
                
                config_df = pd.DataFrame({
                    "Configuração": [
                        "Tamanho do Resumo",
                        "Insights Adicionais",
                        "Alertas Críticos",
                        "Prompt Personalizado",
                        "Modelo de IA",
                        "Idioma"
                    ],
                    "Valor": [
                        tamanho_resumo,
                        "✅ Ativado" if incluir_insights else "❌ Desativado",
                        "✅ Ativado" if incluir_alertas else "❌ Desativado",
                        "✅ Aplicado" if prompt_personalizado else "❌ Não aplicado",
                        "T5 (Transformers)",
                        "Português (PT-BR)"
                    ]
                })
                
                st.dataframe(config_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Seção de histórico/salvamento
            st.subheader("💾 Salvar Resumo")
            
            col_save1, col_save2 = st.columns(2)
            
            with col_save1:
                nome_resumo = st.text_input(
                    "Nome para salvar este resumo",
                    value=f"Resumo_{uploaded_file.name.split('.')[0]}",
                    help="Este nome será usado para identificar o resumo no histórico"
                )
            
            with col_save2:
                tags = st.multiselect(
                    "Tags (opcional)",
                    options=["Urgente", "Projeto", "Relatório", "Análise", "Documentação", "Financeiro"],
                    help="Adicione tags para facilitar a busca futura"
                )
            
            if st.button("💾 Salvar no Histórico", use_container_width=True):
                st.success(f"✅ Resumo '{nome_resumo}' salvo com sucesso! Você poderá acessá-lo futuramente.")
                st.info("📌 *Nota: Funcionalidade de backend será implementada em breve para persistência permanente.*")
    
    # Seção de histórico (mockup)
    st.divider()
    st.subheader("📚 Histórico de Resumos Gerados")
    
    # Mockup de histórico
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
        st.warning("⚠️ *Backend em desenvolvimento - Histórico será persistido no banco de dados em breve*")

# --- Footer ---
st.divider()
st.markdown("""
    <div style='text-align: center; color: #888; padding: 20px;'>
        Dashboard MC Sonae | Grupo 6
    </div>
""", unsafe_allow_html=True)