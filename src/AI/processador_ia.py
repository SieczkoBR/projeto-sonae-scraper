import sqlite3
import os
import re
import logging

# --- Configuração ---
CAMINHO_BANCO = os.path.join("data", "projetos_sonae.db")

# Criar diretório de logs se não existir
os.makedirs("logs", exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "ia_processing.log")),
        logging.StreamHandler()
    ]
)

class ProcessadorIA:
    """
    Classe para processar informações de documentos usando IA.
    Encapsula funcionalidades de extração e análise de texto.
    """
    
    def __init__(self):
        """Inicializa o processador de IA."""
        self.modelo = None
    
    def carregar_modelo(self):
        """Carrega o modelo FLAN-T5 para processamento."""
        self.modelo = carregar_modelo()
        return self.modelo
    
    def extrair_informacoes(self, texto):
        """
        Extrai informações estruturadas de um texto.
        
        Args:
            texto (str): Texto para extrair informações
            
        Returns:
            dict: Dicionário com informações extraídas
        """
        if not texto or len(texto.strip()) < 50:
            return {
                'nome': '',
                'descricao': '',
                'categoria': '',
                'responsavel': '',
                'orcamento': None,
                'data_inicio': None,
                'data_fim': None,
                'tags': ''
            }
        
        try:
            # Extrai conceitos-chave para categorização
            conceitos = extrair_conceitos_chave(texto, max_conceitos=3)
            categoria = conceitos[0] if conceitos else ''
            
            # Extrai frase principal como nome do projeto
            nome = extrair_frase_principal(texto)
            if not nome:
                nome = texto[:100].strip()
            
            # Gera descrição resumida
            descricao = texto[:500].strip()
            
            # Tenta extrair informações estruturadas
            dados = _extrair_dados_contextualizados(texto)
            
            return {
                'nome': nome,
                'descricao': descricao,
                'categoria': categoria,
                'responsavel': dados.get('responsavel', ''),
                'orcamento': dados.get('orcamento'),
                'data_inicio': dados.get('data_inicio'),
                'data_fim': dados.get('data_fim'),
                'tags': ', '.join(conceitos) if conceitos else ''
            }
            
        except Exception as e:
            logging.error(f"Erro ao extrair informações: {e}")
            return {
                'nome': texto[:100].strip() if texto else '',
                'descricao': texto[:500].strip() if texto else '',
                'categoria': '',
                'responsavel': '',
                'orcamento': None,
                'data_inicio': None,
                'data_fim': None,
                'tags': ''
            }

def carregar_modelo():
    """
    Carrega o modelo FLAN-T5 para geração de texto.
    
    Returns:
        Pipeline do modelo ou None se falhar
    """
    try:
        from transformers import pipeline
        
        logging.info("Carregando modelo FLAN-T5...")
        
        modelo = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            device=-1  # CPU
        )
        
        logging.info("Modelo FLAN-T5 carregado com sucesso!")
        return modelo
        
    except Exception as e:
        logging.error(f"Erro ao carregar modelo: {e}")
        return None

def gerar_relatorio_executivo(modelo, conteudo, tamanho, prompt_personalizado="", incluir_graficos=False):
    """
    Gera um relatório executivo completo analisando o conteúdo fornecido.
    
    Args:
        modelo: Modelo FLAN-T5
        conteudo: Conteúdo do arquivo para análise
        tamanho: Nível de detalhe (Muito Curto, Curto, Médio, Longo, Detalhado)
        prompt_personalizado: Instruções adicionais do usuário
        incluir_graficos: Se deve incluir análise de dados para gráficos (não utilizado)
    
    Returns:
        dict: {"texto": str, "dados_graficos": dict}
    """
    try:
        # Limitar conteúdo para não sobrecarregar
        max_chars_map = {
            "Muito Curto": 3000,
            "Curto": 4000,
            "Médio": 5000,
            "Longo": 7000,
            "Detalhado": 10000
        }
        max_chars = max_chars_map.get(tamanho, 5000)
        
        if len(conteudo) > max_chars:
            conteudo = conteudo[:max_chars]
        
        # Determinar instruções de tamanho
        tamanho_instrucoes = {
            "Muito Curto": "Seja MUITO CONCISO. Máximo 3-4 parágrafos curtos.",
            "Curto": "Seja CONCISO. Máximo 5-6 parágrafos.",
            "Médio": "Seja equilibrado. Entre 8-10 parágrafos bem estruturados.",
            "Longo": "Seja DETALHADO. Entre 12-15 parágrafos com análise profunda.",
            "Detalhado": "Seja EXTREMAMENTE DETALHADO. Análise completa e aprofundada com todos os aspectos relevantes."
        }
        
        instrucao_tamanho = tamanho_instrucoes.get(tamanho, "Seja equilibrado e profissional.")
        
        # Construir prompt SIMPLES para FLAN-T5
        prompt = f"""Analise este documento e crie um relatório executivo profissional em português.

Documento:
{conteudo}

Crie um relatório com estas 4 seções:

1. Análise do Documento - Resuma o objetivo e contexto em 2-3 parágrafos

2. Dados e Informações Relevantes - Liste os dados principais:
   - Percentuais e métricas
   - Valores e orçamentos  
   - Datas e prazos
   - Status e responsáveis

3. Insights Estratégicos - Analise riscos, oportunidades e pontos de atenção em 2-3 parágrafos

4. Próximas Ações Recomendadas - Liste 3-5 ações práticas baseadas no documento

{instrucao_tamanho}
{f'Foco especial: {prompt_personalizado}' if prompt_personalizado else ''}

Relatório:"""
        
        # Gerar relatório com FLAN-T5
        logging.info(f"Gerando relatório executivo com FLAN-T5 (tamanho: {tamanho})")
        
        # Configurações de geração
        max_length_map = {
            "Muito Curto": 256,
            "Curto": 512,
            "Médio": 768,
            "Longo": 1024,
            "Detalhado": 1536
        }
        
        resultado = modelo(
            prompt,
            max_length=max_length_map.get(tamanho, 768),
            min_length=100,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )
        
        logging.info("Relatório gerado com sucesso pelo FLAN-T5!")
        texto_gerado = resultado[0]['generated_text']
        
        # Formatação do relatório
        relatorio_formatado = _formatar_relatorio(texto_gerado, conteudo)
        
        # Não gerar gráficos
        return {
            "texto": relatorio_formatado,
            "dados_graficos": None
        }
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório com FLAN-T5: {e}")
        # Retornar análise básica em caso de erro
        return {
            "texto": _gerar_relatorio_basico(conteudo, prompt_personalizado),
            "dados_graficos": None
        }

def _gerar_graficos_analise(conteudo):
    """Gera dados para gráficos com base no conteúdo analisado"""
    import re
    
    graficos = {}
    
    # Palavras-chave que indicam dados IRRELEVANTES (genéricos/exemplos)
    palavras_irrelevantes = [
        'exemplo', 'modelo', 'template', 'amostra', 'ilustração',
        'hipotético', 'fictício', 'simulação', 'teste', 'demo'
    ]
    
    # Tentar extrair percentuais REAIS para gráfico de progresso
    percentuais_com_label = []
    
    # Padrões com PRIORIDADE (mais específicos primeiro, genéricos depois)
    padroes_prioritarios = [
        # Padrão 1: Lista com marcador (mais específico)
        (r'[-•]\s*([A-Za-zÀ-ÿ][^:\n]{10,150}):\s*(\d+)%', 10),
        # Padrão 2: Lista invertida
        (r'[-•]\s*(\d+)%\s+(?:de\s+)?([A-Za-zÀ-ÿ][^\n]{10,100})', 9),
    ]
    
    padroes_genericos = [
        # Padrão 3: Label seguido de percentual (sem marcador)
        (r'([A-Za-zÀ-ÿ][^:\n]{10,100}):\s*(\d+)%', 5),
        # Padrão 4: Percentual seguido de label
        (r'(\d+)%\s+(?:de\s+)?([A-Za-zÀ-ÿ][^\n]{10,80})', 4),
        # Padrão 5: Label com verbo de conclusão
        (r'([A-Za-zÀ-ÿ][^\n]{10,80})\s+(?:está|atingiu|alcançou)?\s*(?:em\s+)?(\d+)%', 3),
    ]
    
    linhas_conteudo = conteudo.split('\n')
    
    # Primeira passagem: tentar padrões prioritários
    for linha in linhas_conteudo:
        linha_lower = linha.lower()
        
        # Ignorar linhas com palavras irrelevantes
        if any(palavra in linha_lower for palavra in palavras_irrelevantes):
            continue
        
        # Ignorar linha se for apenas título genérico (como "concluído: 100%")
        if re.match(r'^\s*[a-zç]{1,15}\s*:\s*\d+%\s*$', linha.strip(), re.IGNORECASE):
            continue
        
        for padrao, prioridade in padroes_prioritarios:
            matches = re.findall(padrao, linha, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    label = match[0].strip() if not match[0].isdigit() else match[1].strip()
                    valor = match[1] if not match[0].isdigit() else match[0]
                    
                    try:
                        valor_num = int(valor)
                        if 0 < valor_num <= 100:
                            # Limpar sufixos desnecessários do label
                            label_limpo = re.sub(r'\s+(concluído|concluída|finalizado|finalizada|completo|completa).*$', '', label, flags=re.IGNORECASE)
                            label_limpo = re.sub(r'[:\-]$', '', label_limpo).strip()
                            label_limpo = label_limpo[:60]
                            
                            # Validar tamanho mínimo
                            if len(label_limpo) >= 8 and re.search(r'[a-zA-ZÀ-ÿ]{5,}', label_limpo):
                                # Evitar duplicatas
                                if not any(p['label'].lower() == label_limpo.lower() for p in percentuais_com_label):
                                    percentuais_com_label.append({
                                        'label': label_limpo,
                                        'valor': valor_num,
                                        'prioridade': prioridade
                                    })
                    except:
                        pass
    
    # Segunda passagem: se não encontrou itens suficientes, usar padrões genéricos
    if len(percentuais_com_label) < 2:
        for linha in linhas_conteudo:
            linha_lower = linha.lower()
            
            if any(palavra in linha_lower for palavra in palavras_irrelevantes):
                continue
            
            if re.match(r'^\s*[a-zç]{1,15}\s*:\s*\d+%\s*$', linha.strip(), re.IGNORECASE):
                continue
            
            for padrao, prioridade in padroes_genericos:
                matches = re.findall(padrao, linha, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        label = match[0].strip() if not match[0].isdigit() else match[1].strip()
                        valor = match[1] if not match[0].isdigit() else match[0]
                        
                        try:
                            valor_num = int(valor)
                            if 0 < valor_num <= 100:
                                label_limpo = re.sub(r'\s+(concluído|concluída|finalizado|finalizada|completo|completa).*$', '', label, flags=re.IGNORECASE)
                                label_limpo = re.sub(r'[:\-]$', '', label_limpo).strip()
                                label_limpo = label_limpo[:60]
                                
                                # Para padrões genéricos, ser um pouco mais flexível no tamanho
                                if len(label_limpo) >= 5 and re.search(r'[a-zA-ZÀ-ÿ]{3,}', label_limpo):
                                    if not any(p['label'].lower() == label_limpo.lower() for p in percentuais_com_label):
                                        percentuais_com_label.append({
                                            'label': label_limpo,
                                            'valor': valor_num,
                                            'prioridade': prioridade
                                        })
                        except:
                            pass
    
    # Gerar gráfico apenas se houver dados válidos (mínimo 2, máximo 8)
    if len(percentuais_com_label) >= 2:
        # Ordenar por prioridade primeiro, depois por valor
        percentuais_com_label = sorted(percentuais_com_label, key=lambda x: (x['prioridade'], x['valor']), reverse=True)[:8]
        
        valores = [p['valor'] for p in percentuais_com_label]
        labels = [p['label'] for p in percentuais_com_label]
        
        graficos['progresso'] = {
            'tipo': 'barra',
            'valores': valores,
            'labels': labels,
            'titulo': 'Indicadores de Progresso do Projeto',
            'descricao': 'Percentuais de conclusão das diferentes etapas identificadas no documento. Estes dados representam o estado atual do projeto conforme documentado.'
        }
    
    return graficos if graficos else None

def _dividir_em_secoes(texto):
    """Divide o texto em seções lógicas baseado em pontos, números ou tópicos"""
    import re
    
    # Tentar identificar seções numeradas (1., 2., etc)
    secoes_numeradas = re.split(r'\n*\d+\.\s+', texto)
    if len(secoes_numeradas) > 2:  # Se encontrou seções numeradas
        return [s.strip() for s in secoes_numeradas if s.strip()]
    
    # Tentar identificar por quebras de parágrafo duplas
    paragrafos = texto.split('\n\n')
    if len(paragrafos) > 1:
        return [p.strip() for p in paragrafos if p.strip()]
    
    # Tentar dividir por sentenças e agrupar
    sentencas = re.split(r'(?<=[.!?])\s+', texto)
    
    if len(sentencas) <= 2:
        return [texto]
    
    # Agrupar em blocos de 2-3 sentenças
    secoes = []
    temp_secao = []
    
    for i, sentenca in enumerate(sentencas):
        temp_secao.append(sentenca)
        if len(temp_secao) >= 2 or i == len(sentencas) - 1:
            secoes.append(' '.join(temp_secao))
            temp_secao = []
    
    return secoes

def _formatar_relatorio(texto, conteudo_original):
    """
    Formata e estrutura o relatório gerado pelo FLAN-T5
    """
    import re
    
    # Se já tem estrutura de seções, retornar
    if '##' in texto or '**Análise' in texto:
        return texto
    
    # Limpar e capitalizar
    texto = texto.strip()
    if texto and len(texto) > 0:
        texto = texto[0].upper() + texto[1:]
    
    # Dividir texto em frases para criar parágrafos
    frases = re.split(r'\. ', texto)
    paragrafos = []
    paragrafo_atual = []
    
    for i, frase in enumerate(frases):
        paragrafo_atual.append(frase.strip())
        # Criar novo parágrafo a cada 2-3 frases
        if (i + 1) % 2 == 0 or i == len(frases) - 1:
            if paragrafo_atual:
                paragrafos.append('. '.join(paragrafo_atual) + ('.' if not paragrafo_atual[-1].endswith('.') else ''))
                paragrafo_atual = []
    
    texto_formatado = '\n\n'.join(paragrafos)
    
    # Extrair dados do documento original
    dados_extraidos = _extrair_dados_contextualizados(conteudo_original)
    
    # Estruturar relatório
    relatorio = f"""## Análise do Documento

{texto_formatado}

---

## Dados e Informações Relevantes

"""
    
    # Adicionar dados extraídos
    if dados_extraidos:
        for dado in dados_extraidos:
            if dado.get('categoria') and dado.get('valores'):
                relatorio += f"**{dado['categoria']}**\n\n"
                for valor in dado['valores'][:5]:  # Limitar a 5 itens
                    relatorio += f"- {valor}\n"
                relatorio += "\n"
    else:
        relatorio += "Dados estruturados não identificados automaticamente.\n\n"
    
    relatorio += """---

## Insights Estratégicos

Baseado na análise do documento:

- O projeto apresenta informações estruturadas que requerem atenção executiva
- Recomenda-se validação dos dados apresentados para decisões estratégicas
- Pontos de atenção devem ser priorizados conforme impacto e urgência

---

## Próximas Ações Recomendadas

1. Revisar dados e métricas apresentadas no documento
2. Identificar prioridades e ações críticas
3. Estabelecer indicadores de acompanhamento
4. Documentar decisões e próximos passos
5. Agendar revisão de progresso

"""
    
    return relatorio

def _extrair_dados_contextualizados(texto):
    """Extrai dados numéricos com contexto real do texto"""
    import re
    
    dados = []
    
    # Palavras-chave que indicam dados IRRELEVANTES
    palavras_irrelevantes = [
        'exemplo', 'modelo', 'template', 'amostra', 'ilustração',
        'hipotético', 'fictício', 'simulação', 'teste', 'demo',
        'padrão', 'genérico', 'default'
    ]
    
    # Buscar percentuais com contexto mais amplo
    linhas = texto.split('\n')
    percentuais_encontrados = []
    
    for linha in linhas:
        # Ignorar linhas inteiras com palavras irrelevantes
        linha_lower = linha.lower()
        if any(palavra in linha_lower for palavra in palavras_irrelevantes):
            continue
        
        # Ignorar linhas genéricas tipo "concluído: 100%" (títulos curtos)
        if re.match(r'^\s*[a-zç]{1,15}\s*:\s*\d+%\s*$', linha.strip(), re.IGNORECASE):
            continue
        
        # PRIORIDADE 1: Procurar padrões de lista com percentual
        # "- Desenvolvimento da estrutura: 100% concluído"
        match_lista = re.search(r'[-•]\s*([^:\n]{10,150}):\s*(\d+)%', linha, re.IGNORECASE)
        if match_lista:
            label = match_lista.group(1).strip()
            valor = match_lista.group(2)
            
            # Limpar sufixos desnecessários
            label_limpo = re.sub(r'\s+(concluído|concluída|finalizado|finalizada|completo|completa).*$', '', label, flags=re.IGNORECASE)
            label_limpo = label_limpo.strip()
            
            # Validar
            if len(label_limpo) >= 8 and re.search(r'[a-zA-ZÀ-ÿ]{5,}', label_limpo):
                contexto = f"{label_limpo}: {valor}%"
                
                # Evitar duplicatas
                if not any(p['valor'] == valor and label_limpo.lower() in p['contexto'].lower() for p in percentuais_encontrados):
                    percentuais_encontrados.append({
                        'valor': valor,
                        'contexto': contexto,
                        'prioridade': 10
                    })
            continue
        
        # PRIORIDADE 2: Procurar outros padrões de percentual com contexto
        matches = re.finditer(r'(.{0,80})(\d+)%(.{0,80})', linha, re.IGNORECASE)
        for match in matches:
            contexto_antes = match.group(1).strip()
            valor = match.group(2)
            contexto_depois = match.group(3).strip()
            
            # Ignorar percentuais de 0% sem contexto relevante
            if valor == '0' and not any(palavra in linha_lower for palavra in ['progresso', 'conclusão', 'andamento', 'completo']):
                continue
            
            # Montar contexto completo
            contexto_completo = f"{contexto_antes} {valor}% {contexto_depois}".strip()
            
            # Limpar contexto de caracteres especiais no início/fim
            contexto_completo = re.sub(r'^[:\-\s]+|[:\-\s]+$', '', contexto_completo)
            
            # Validar que o contexto tem pelo menos algum texto significativo
            texto_sem_percentual = contexto_completo.replace(f'{valor}%', '').strip()
            if len(texto_sem_percentual) < 8:  # Reduzido de 10 para 8 para ser mais flexível
                continue
            
            # Validar que tem texto alfabético real (não apenas números/símbolos)
            if not re.search(r'[a-zA-ZÀ-ÿ]{4,}', texto_sem_percentual):  # Reduzido de 5 para 4
                continue
            
            # Evitar duplicatas exatas ou muito similares
            if not any(p['valor'] == valor and p['contexto'][:40] == contexto_completo[:40] for p in percentuais_encontrados):
                percentuais_encontrados.append({
                    'valor': valor,
                    'contexto': contexto_completo[:200],
                    'prioridade': 5
                })
    
    if percentuais_encontrados:
        # Ordenar por prioridade e limitar a 8 itens mais relevantes
        percentuais_encontrados = sorted(percentuais_encontrados, key=lambda x: x['prioridade'], reverse=True)[:8]
        
        valores = []
        for p in percentuais_encontrados:
            contexto_limpo = p['contexto'].replace('\n', ' ').strip()
            if contexto_limpo:
                valores.append(f"{p['valor']}% → {contexto_limpo}")
        
        if valores:
            dados.append({
                'categoria': 'Indicadores de Progresso',
                'descricao': 'Percentuais e métricas identificados no documento:',
                'valores': valores
            })
    
    # Buscar informações de prazo e status (evitar duplicatas e dados genéricos)
    status_info = {}
    padroes_status = [
        (r'status:?\s*([^\n.]{5,100})', 'Status'),
        (r'situação:?\s*([^\n.]{5,100})', 'Situação'),
        (r'responsável:?\s*([^\n.]{3,80})', 'Responsável'),
    ]
    
    for linha in linhas:
        # Ignorar linhas com palavras irrelevantes
        if any(palavra in linha.lower() for palavra in palavras_irrelevantes):
            continue
            
        for padrao, categoria in padroes_status:
            if categoria not in status_info:  # Evitar duplicatas de categoria
                matches = re.findall(padrao, linha, re.IGNORECASE)
                if matches:
                    info = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    info_limpa = info.strip()[:150]
                    
                    # Validar que não é genérico demais
                    if info_limpa and len(info_limpa) > 5:
                        # Deve conter letras reais
                        if re.search(r'[a-zA-ZÀ-ÿ]{3,}', info_limpa):
                            status_info[categoria] = info_limpa
    
    if status_info:
        valores_formatados = [f"{cat}: {val}" for cat, val in status_info.items()]
        dados.append({
            'categoria': 'ℹ️ Informações do Projeto',
            'descricao': 'Detalhes identificados no documento:',
            'valores': valores_formatados
        })
    
    # Buscar datas específicas (sem duplicatas)
    datas_encontradas = set()
    padroes_data = [
        r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # Datas dd/mm/yyyy
    ]
    
    for linha in linhas:
        # Ignorar linhas com palavras irrelevantes
        if any(palavra in linha.lower() for palavra in palavras_irrelevantes):
            continue
            
        for padrao in padroes_data:
            matches = re.findall(padrao, linha)
            for data in matches[:5]:
                datas_encontradas.add(data)
    
    if datas_encontradas and len(datas_encontradas) <= 10:  # Limitar para evitar lixo
        dados.append({
            'categoria': 'Prazos e Datas',
            'descricao': 'Datas identificadas no documento:',
            'valores': sorted(list(datas_encontradas))[:5]
        })
    
    return dados if dados else None

def _extrair_palavras_chave(texto):
    """Extrai palavras-chave relevantes e específicas do texto"""
    import re
    from collections import Counter
    
    # Lista expandida de stop words
    stop_words = {'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'você', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'sido', 'sendo', 'estar', 'sobre', 'pode', 'fazer', 'cada', 'outro', 'outra', 'outros', 'outras', 'bem', 'ainda', 'onde', 'enquanto', 'antes', 'após', 'todas', 'todos', 'qualquer', 'algum', 'alguma', 'alguns', 'algumas', 'nenhum', 'nenhuma', 'mesmo', 'mesma', 'mesmos', 'mesmas'}
    
    # Termos genéricos de documentos que devem ser filtrados
    termos_genericos = {'documento', 'relatório', 'análise', 'arquivo', 'conteúdo', 'informação', 'dados', 'sistema', 'projeto', 'seguinte', 'execução', 'exemplo', 'forma', 'parte', 'através', 'devido', 'conforme', 'segundo', 'durante', 'desta', 'deste', 'dessa', 'desse'}
    
    # Extrair apenas substantivos e termos técnicos (5+ caracteres)
    palavras = re.findall(r'\b[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][a-záàâãéèêíïóôõöúçñ]{4,}\b', texto)
    
    # Filtrar stop words e termos genéricos
    palavras_filtradas = [
        p.lower() for p in palavras 
        if p.lower() not in stop_words and p.lower() not in termos_genericos
    ]
    
    # Contar frequência
    contador = Counter(palavras_filtradas)
    
    # Priorizar palavras que aparecem mais de uma vez
    palavras_relevantes = [
        palavra for palavra, freq in contador.most_common(20)
        if freq >= 2  # Aparecem pelo menos 2 vezes
    ]
    
    # Se não houver palavras repetidas suficientes, pegar as mais comuns
    if len(palavras_relevantes) < 5:
        palavras_relevantes = [palavra for palavra, _ in contador.most_common(10)]
    
    # Capitalizar primeira letra
    return [palavra.capitalize() for palavra in palavras_relevantes[:10]]

def _gerar_relatorio_basico(conteudo, prompt_personalizado):
    """Gera um relatório básico caso a IA falhe"""
    
    # Extrair primeiras frases do conteúdo
    frases = conteudo.split('.')[:5]
    resumo_basico = '. '.join(frases) + '.'
    
    relatorio = f"""# Relatório Executivo

## Resumo do Documento

{resumo_basico}

## Análise

O documento apresenta informações relevantes que requerem análise detalhada. 
Principais aspectos identificados:

- Conteúdo estruturado com dados importantes
- Informações que necessitam de avaliação estratégica
- Pontos que podem impactar decisões futuras

"""
    
    if prompt_personalizado:
        relatorio += f"""## Foco Solicitado

{prompt_personalizado}

"""
    
    relatorio += """---

*Nota: Este é um relatório básico gerado automaticamente. Para análise mais profunda, 
recomenda-se revisão manual do documento.*
"""
    
    return relatorio


def extrair_conceitos_chave(texto, max_conceitos=3):
    """
    Extrai os conceitos-chave mais importantes de um texto.
    
    Args:
        texto: Texto para análise
        max_conceitos: Número máximo de conceitos a extrair
        
    Returns:
        list: Lista de conceitos-chave
    """
    # Palavras-chave técnicas relevantes
    palavras_relevantes = [
        'dados', 'análise', 'integração', 'riscos', 'gestão', 'monitoramento',
        'indicadores', 'desempenho', 'automação', 'ETL', 'API', 'dashboard',
        'relatórios', 'métricas', 'qualidade', 'consistência', 'alertas',
        'governança', 'compliance', 'estratégia', 'otimização', 'processos',
        'eficiência', 'performance', 'confiabilidade', 'segurança'
    ]
    
    texto_lower = texto.lower()
    conceitos_encontrados = []
    
    for palavra in palavras_relevantes:
        if palavra in texto_lower and palavra not in conceitos_encontrados:
            conceitos_encontrados.append(palavra)
            if len(conceitos_encontrados) >= max_conceitos:
                break
    
    return conceitos_encontrados


def extrair_frase_principal(texto):
    """
    Extrai a primeira frase significativa do texto.
    
    Args:
        texto: Texto para análise
        
    Returns:
        str: Primeira frase relevante
    """
    # Dividir em frases
    frases = re.split(r'[.!?]\s+', texto)
    
    # Retornar a primeira frase com mais de 20 caracteres
    for frase in frases:
        if len(frase.strip()) > 20:
            return frase.strip()
    
    return texto[:150].strip()


def gerar_insight_estruturado(texto_resumo, texto_desafios):
    """
    Gera um insight estruturado com gramática perfeita usando templates e extração de conceitos.
    
    Args:
        texto_resumo: Texto do resumo executivo
        texto_desafios: Texto dos principais desafios
        
    Returns:
        str: Insight gerado com gramática correta
    """
    try:
        # Extrair conceitos-chave do resumo
        conceitos_resumo = extrair_conceitos_chave(texto_resumo, max_conceitos=3)
        
        # Extrair conceitos-chave dos desafios
        conceitos_desafios = extrair_conceitos_chave(texto_desafios, max_conceitos=2)
        
        # Extrair frase principal do resumo
        frase_principal = extrair_frase_principal(texto_resumo)
        
        # Construir insight estruturado
        partes_insight = []
        
        # Parte 1: Foco principal
        if conceitos_resumo:
            if len(conceitos_resumo) == 1:
                conceitos_str = conceitos_resumo[0]
            elif len(conceitos_resumo) == 2:
                conceitos_str = f"{conceitos_resumo[0]} e {conceitos_resumo[1]}"
            else:
                conceitos_str = ", ".join(conceitos_resumo[:-1]) + f" e {conceitos_resumo[-1]}"
            
            partes_insight.append(f"Projeto focado em {conceitos_str}")
        else:
            # Usar frase principal como fallback
            partes_insight.append(frase_principal[:100])
        
        # Parte 2: Desafios principais
        if conceitos_desafios:
            if len(conceitos_desafios) == 1:
                desafios_str = conceitos_desafios[0]
            else:
                desafios_str = f"{conceitos_desafios[0]} e {conceitos_desafios[1]}"
            
            partes_insight.append(f"com desafios relacionados a {desafios_str}")
        
        # Parte 3: Objetivo estratégico (baseado no contexto)
        if 'dados' in conceitos_resumo or 'análise' in conceitos_resumo:
            partes_insight.append("visando suporte à tomada de decisão estratégica")
        elif 'riscos' in conceitos_resumo or 'gestão' in conceitos_resumo:
            partes_insight.append("para garantir operações seguras e eficientes")
        elif 'indicadores' in conceitos_resumo or 'monitoramento' in conceitos_resumo:
            partes_insight.append("permitindo acompanhamento contínuo de resultados e performance")
        elif 'automação' in conceitos_resumo or 'processos' in conceitos_resumo:
            partes_insight.append("otimizando processos e aumentando a eficiência operacional")
        
        # Combinar todas as partes
        insight = ", ".join(partes_insight) + "."
        
        # Garantir primeira letra maiúscula
        insight = insight[0].upper() + insight[1:]
        
        return insight
        
    except Exception as e:
        logging.error(f"Erro ao gerar insight estruturado: {str(e)}")
        return "Insight não disponível no momento."

# --- Função de Conexão (Helper) ---
def get_db_connection():
    try:
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.row_factory = sqlite3.Row # Para acessar por nome
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

# --- ETAPA 2: Processar os Dados ---
def gerar_insight_para_projeto(projeto_id=None, texto_resumo=None, texto_desafios=None):
    """
    Gera insight estruturado para um projeto específico
    
    Args:
        projeto_id: ID do projeto (se fornecido, busca do banco)
        texto_resumo: Texto do resumo executivo (opcional)
        texto_desafios: Texto dos desafios (opcional)
    
    Returns:
        String com o insight gerado ou None se falhar
    """
    # Se projeto_id foi fornecido, buscar do banco
    if projeto_id:
        conexao = get_db_connection()
        if conexao is None:
            return None
        
        try:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT resumo_executivo, principais_desafios 
                FROM projetos WHERE id = ?
            """, (projeto_id,))
            
            projeto = cursor.fetchone()
            if projeto:
                texto_resumo = projeto['resumo_executivo']
                texto_desafios = projeto['principais_desafios']
        finally:
            conexao.close()
    
    # Verificar se temos texto para processar
    if not texto_resumo and not texto_desafios:
        logging.warning("Nenhum texto disponível para gerar insight")
        return None
    
    # Usar valores padrão se algum estiver vazio
    if not texto_resumo:
        texto_resumo = "Projeto em desenvolvimento"
    if not texto_desafios:
        texto_desafios = "Sem desafios registrados"
    
    try:
        # Gerar insight estruturado
        insight_texto = gerar_insight_estruturado(texto_resumo, texto_desafios)
        logging.info(f"Insight gerado: {insight_texto}")
        
        # Se projeto_id foi fornecido, salvar no banco
        if projeto_id:
            conexao = get_db_connection()
            if conexao:
                try:
                    cursor = conexao.cursor()
                    cursor.execute(
                        "UPDATE projetos SET resumo_ia = ? WHERE id = ?",
                        (insight_texto, projeto_id)
                    )
                    conexao.commit()
                    logging.info(f"Insight salvo para projeto ID {projeto_id}")
                finally:
                    conexao.close()
        
        return insight_texto
        
    except Exception as e:
        logging.error(f"Erro ao gerar insight: {e}")
        return None

def gerar_insights():
    """Processa todos os projetos sem insights de IA"""
    conexao = get_db_connection()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()
        
        # Selecionamos projetos que têm um resumo, mas AINDA NÃO têm um insight de IA
        cursor.execute("""
            SELECT id, nome_projeto, resumo_executivo, principais_desafios 
            FROM projetos 
            WHERE resumo_ia IS NULL 
            AND (resumo_executivo IS NOT NULL OR principais_desafios IS NOT NULL)
        """)
        
        projetos_para_processar = cursor.fetchall()
        
        if not projetos_para_processar:
            print("Nenhum projeto novo para processar. O banco já está atualizado.")
            return

        print(f"Encontrados {len(projetos_para_processar)} projetos para gerar insights...")

        for projeto in projetos_para_processar:
            insight_texto = gerar_insight_para_projeto(
                projeto_id=projeto['id'],
                texto_resumo=projeto['resumo_executivo'],
                texto_desafios=projeto['principais_desafios']
            )
            
            if insight_texto:
                print(f"Insight gerado para '{projeto['nome_projeto']}': {insight_texto}")

        conexao.commit()
        print(f"Sucesso! {len(projetos_para_processar)} projetos atualizados com insights.")

    except Exception as e:
        print(f"ERRO durante o processamento dos insights: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco fechada.")

# --- Executa a função principal ---
if __name__ == "__main__":
    gerar_insights()