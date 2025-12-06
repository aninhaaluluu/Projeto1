import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("⚖️ Simulador de Dosimetria da Pena (Versão 2.0) ⚖️")
st.write("**Calculadora completa da dosimetria penal conforme Art. 68 do CP**")

# --- Constante para a URL do arquivo CSV ---
CSV_URL = 'https://raw.githubusercontent.com/matheusasharosilva-debug/Dosimetria-penal2/refs/heads/main/crimes_cp_final_sem_art68.csv'
# ------------------------------------------

@st.cache_data
def processar_dados_crimes(df):
    """
    Processa os dados dos crimes, CONVERTE TODAS AS PENAS PARA ANOS 
    e trata erros de tipo de dados.
    """
    if df.empty:
        return {}
        
    crimes_dict = {}
    
    for idx, row in df.iterrows():
        
        # 1. DEFINIÇÃO DAS VARIÁVEIS DE TEXTO (para resolver "artigo_completo is not defined")
        artigo_base = row.get('Artigo_Base', '') if pd.notna(row.get('Artigo_Base')) else ''
        artigo_completo = row.get('Artigo_Completo', '') if pd.notna(row.get('Artigo_Completo')) else artigo_base
        descricao = row.get('Descricao_Crime', '') if pd.notna(row.get('Descricao_Crime')) else ''
        tipo_penal = row.get('Tipo_Penal_Estrutural', 'Crime Base (Caput)') if pd.notna(row.get('Tipo_Penal_Estrutural')) else 'Crime Base (Caput)'
        
        # Inicializa variáveis para evitar erros
        pena_min_anos = 0
        pena_max_anos = 0
        pena_min_valor = 0
        pena_max_valor = 0
        pena_min_unidade = 'ano'
        pena_max_unidade = 'ano'
        
        # 2. DEFINIÇÃO E TRATAMENTO DE VALORES NUMÉRICOS E UNIDADES
        try:
            # Garante que o valor é um float
            pena_min_valor = float(row.get('Pena_Minima_Valor', 0))
            pena_max_valor = float(row.get('Pena_Maxima_Valor', 0))
            
            # Garante que a unidade é uma string antes de chamar .lower() (CORREÇÃO DO ERRO 'float' object)
            pena_min_unidade = str(row.get('Pena_Minima_Unidade', 'mês')).lower()
            pena_max_unidade = str(row.get('Pena_Maxima_Unidade', 'mês')).lower()

        except ValueError:
            # Se a conversão numérica falhar (dados sujos), pula esta linha
            continue

        # 3. CONVERSÃO PARA ANOS
        def converter_para_anos(valor, unidade):
            if unidade == 'mês':
                return valor / 12
            elif unidade == 'dia':
                return valor / 360  # 360 dias por ano
            else: # Anos, ano, etc.
                return valor

        pena_min_anos = converter_para_anos(pena_min_valor, pena_min_unidade)
        pena_max_anos = converter_para_anos(pena_max_valor, pena_max_unidade)
        
        # Garante que o mínimo não é maior que o máximo
        if pena_min_anos > pena_max_anos:
             pena_min_anos = 0 
            
        # 4. CRIAÇÃO DA CHAVE E DADOS (Só se tiver artigo e descrição)
        if artigo_completo and descricao:
            chave = f"Art. {artigo_completo} - {descricao[:80]}{'...' if len(descricao) > 80 else ''}"
            
            crimes_dict[chave] = {
                'artigo': artigo_completo,
                'artigo_base': artigo_base,
                'descricao_completa': descricao,
                'pena_min': pena_min_anos,
                'pena_max': pena_max_anos,
                'tipo_penal': tipo_penal,
                'pena_min_original': pena_min_valor,
                'pena_max_original': pena_max_valor,
                'unidade_original_min': pena_min_unidade,
                'unidade_original_max': pena_max_unidade
            }
    
    return crimes_dict

# --- Carregar dados DIRETAMENTE DA URL ---
df = pd.DataFrame()
crimes_data = {}
carregamento_sucesso = False

try:
    codificacoes = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
    
    for encoding in codificacoes:
        try:
            # Tenta carregar o arquivo
            df = pd.read_csv(CSV_URL, encoding=encoding, sep=',')
            st.success(f"✅ Dados carregados com sucesso! (Codificação: {encoding})")
            carregamento_sucesso = True
            break
        except Exception:
            continue
    
    if carregamento_sucesso:
        crimes_data = processar_dados_crimes(df)
        if not crimes_data:
            st.error("❌ Os dados foram carregados, mas não foi possível processar nenhum crime. Verifique se o formato das colunas está correto.")
            carregamento_sucesso = False

except Exception as e:
    # Este erro só será exibido se o carregamento do CSV falhar completamente
    st.error(f"❌ Erro ao carregar arquivo da URL: {e}")
    carregamento_sucesso = False

# --- Fim do Carregamento ---

# Sidebar
st.sidebar.header("💡 Sobre")
st.sidebar.write("**Base Legal:** Art. 68 do Código Penal - Fases: 1.Pena base 2.Atenuantes/Agravantes 3.Majorantes/Minorantes 4.Cálculo 5.Regime 6.Substituição")
st.sidebar.write(f"**📊 Crimes carregados:** {len(crimes_data)}")

# Busca na sidebar
st.sidebar.write("**🔍 Buscar crime:**")
busca = st.sidebar.text_input("Digite o artigo ou descrição:")

if busca and crimes_data:
    crimes_filtrados = {k: v for k, v in crimes_data.items() if busca.lower() in k.lower()}
    st.sidebar.write(f"**Resultados ({len(crimes_filtrados)}):**")
    for chave in list(crimes_filtrados.keys())[:5]:
        crime_info = crimes_filtrados[chave]
        st.sidebar.write(f"**{crime_info['artigo']}** - Pena: {crime_info['pena_min']:.1f}-{crime_info['pena_max']:.1f} anos")

# Se não há dados carregados, mostrar mensagem
if not crimes_data or not carregamento_sucesso:
    st.warning("""
    **⚠️ Aguardando carregamento do dataset**
    
    Para usar o simulador:
    1. Certifique-se que o arquivo `crimes_cp_final_sem_art68.csv` está na raiz do seu repositório GitHub.
    2. Verifique se as colunas estão no formato correto.
    """)
    st.stop()

# VARIÁVEIS DE CÁLCULO INICIAL (definidas após o carregamento)
crime_selecionado = list(crimes_data.keys())[0]
min_pena = 0
max_pena = 0

# ------------------------------------------------------------------
## 1️⃣ Fase 1: Pena Base e Circunstâncias (Art. 59 CP)
# ------------------------------------------------------------------

st.header("1️⃣ Fase 1: Pena Base e Circunstâncias (Art. 59 CP)")
col1, col2 = st.columns([2, 1])

with col1:
    crime_selecionado = st.selectbox("Selecione o Crime:", options=list(crimes_data.keys()), format_func=lambda x: x)
    crime_info = crimes_data[crime_selecionado]
    min_pena = crime_info['pena_min'] # Limite Mínimo Legal (em anos)
    max_pena = crime_info['pena_max'] # Limite Máximo Legal (em anos)
    
    st.write(f"**Artigo:** {crime_info['artigo']}")
    st.write(f"**Tipo penal:** {crime_info['tipo_penal']}")
    st.write(f"**Descrição:** {crime_info['descricao_completa']}")
    st.write(f"**Pena original:** {crime_info['pena_min_original']} {crime_info['unidade_original_min']} a {crime_info['pena_max_original']} {crime_info['unidade_original_max']}")

with col2:
    # Cálculo do 'Quantum' da pena para a fase 1 (Art. 59)
    range_pena = max_pena - min_pena 
    
    # Simulação da avaliação das 8 Circunstâncias Judiciais do Art. 59
    circunstancia = st.slider("Circunstâncias Judiciais Desfavoráveis (Art. 59):", 0, 8, 0, help="Número de circunstâncias desfavoráveis. Aumenta a pena-base dentro do intervalo legal.")
    
    # Cálculo do 'Aumento por Circunstância'
    aumento_por_circunstancia = (range_pena / 8) if range_pena > 0 else 0
    
    pena_base_inicial = min_pena
    ajuste_circunstancia = circunstancia * aumento_por_circunstancia
    pena_base_ajustada = min(max_pena, pena_base_inicial + ajuste_circunstancia) 

    st.write(f"**Pena prevista (Mín-Máx):** {min_pena:.1f} a {max_pena:.1f} anos")
    st.write(f"**Pena base inicial:** {pena_base_inicial:.1f} anos")
    st.write(f"**Ajuste (Circunstâncias {circunstancia}/8):** +{ajuste_circunstancia:.1f} anos")
    st.success(f"**PENA BASE FINAL: {pena_base_ajustada:.1f} anos**")

---
## 2️⃣ Fase 2: Atenuantes e Agravantes Gerais (Pena Provisória)
# ------------------------------------------------------------------

st.header("2️⃣ Fase 2: Atenuantes e Agravantes Gerais (Art. 61, 62 e 65 CP)")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔽 Atenuantes (Art. 65 CP)")
    atenuantes = st.multiselect("Selecione as atenuantes:", [
        "Menor de 21 anos na data do fato (idade)",
        "Maior de 70 anos na data da sentença (idade)",
        "Desconhecimento da lei",
        "Motivo de relevante valor social ou moral",
        "Arrependimento espontâneo eficiente",
        "Reparação do dano antes do julgamento",
        "Coação a que podia resistir",
        "Cumprimento de ordem superior",
        "Violenta emoção por ato injusto da vítima",
        "Confissão espontânea perante autoridade (Súmula 545 STJ)",
        "Influência de multidão em tumulto (sem provocação)",
        "Circunstância relevante não prevista em lei (Art. 66)"
    ])

with col2:
    st.subheader("🔼 Agravantes (Art. 61 e 62 CP)")
    agravantes = st.multiselect("Selecione as agravantes:", [
        "Reincidência (Art. 61, I)",
        "Motivo fútil ou torpe",
        "Facilitar/assegurar execução de outro crime",
        "Traição, emboscada ou dissimulação",
        "Emprego de veneno, fogo, explosivo, tortura",
        "Meio insidioso ou cruel",
        "Perigo comum resultante",
        "Crime contra ascendente/descendente/irmão/cônjuge",
        "Abuso de autoridade",
        "Abuso de relações domésticas/coabitação/hospitalidade",
        "Violência contra a mulher",
        "Abuso de poder ou violação de dever profissional",
        "Crime contra criança/idoso/enfermo/mulher grávida",
        "Ofendido sob proteção imediata da autoridade",
        "Ocasião de calamidade pública/desgraça particular",
        "Embriaguez preordenada",
        "Nas dependências de instituição de ensino",
        "Promotor/organizador do concurso de pessoas (Art. 62)",
        "Coação/indução à execução do crime (Art. 62)",
        "Instigação/determinação a pessoa sob autoridade (Art. 62)",
        "Execução mediante paga ou promessa de recompensa (Art. 62)"
    ])

---
## 3️⃣ Fase 3: Causas de Aumento/Diminuição
# ------------------------------------------------------------------

st.header("3️⃣ Fase 3: Causas de Aumento/Diminuição (Art. 68, III CP)")
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Majorantes (Causas de Aumento)")
    majorantes = st.multiselect("Causas de aumento (majorantes):", [
        "Uso de arma (ex: 1/6 a 1/2)",  
        "Violência grave (ex: 1/3 a 2/3)",  
        "Concurso de 2+ pessoas (ex: 1/4 a 1/2)",  
        "Restrição à liberdade (ex: 1/6 a 1/3)",  
        "Abuso de confiança (ex: 1/6 a 1/3)",
        "Aumento por continuidade delitiva (fracionado)",
        "Aumento específico do tipo penal"
    ])
with col2:
    st.subheader("📉 Minorantes (Causas de Diminuição)")
    minorantes = st.multiselect("Causas de diminuição (minorantes):", [
        "Valor ínfimo do dano (ex: 1/6 a 1/3)",  
        "Arrependimento posterior (ex: 1/6 a 1/3)",  
        "Circunstâncias atenuantes não previstas (ex: 1/6 a 1/3)",
        "Diminuição específica do tipo penal",
        "Causa de diminuição de culpabilidade (ex: 1/3 a 2/3)"
    ])

---
## 4️⃣ Fase 4: Cálculo Final da Pena (Sistema Trifásico)
# ------------------------------------------------------------------

st.header("4️⃣ Fase 4: Cálculo Final da Pena (Sistema Trifásico)")

if st.button("🎯 Calcular Pena Definitiva", type="primary"):
    
    # 1. PENA BASE (Resultado da Fase 1)
    pena_provisoria = pena_base_ajustada
    calculo_detalhado = f"| Etapa | Valor | Ajuste |\n|-------|-------|---------|\n| **Pena Base (1ª Fase)** | {pena_base_ajustada:.1f} anos | ({circunstancia} Circ. Desf.) |\n"
    
    aplicou_sumula_231_atenuante = False
    
    # 2. SEGUNDA FASE: ATENUANTES E AGRAVANTES
    
    # Fração de ajuste padrão (1/6 da Pena Base)
    ajuste_fracao_2fase = pena_base_ajustada * (1/6)
    
    # Aplicar Atenuantes (com LIMITE MÍNIMO LEGAL - Súmula 231)
    ajustes_atenuantes = []
    for i, atenuante in enumerate(atenuantes, 1):
        reducao = ajuste_fracao_2fase
        if (pena_provisoria - reducao) >= min_pena:
            pena_provisoria -= reducao
            ajustes_atenuantes.append(reducao)
            calculo_detalhado += f"| Atenuante {i} | {pena_provisoria:.1f} anos | -{reducao:.1f} anos (1/6 PB) |\n"
        else:
            reducao_possivel = pena_provisoria - min_pena
            if reducao_possivel > 0.05: 
                pena_provisoria = min_pena
                ajustes_atenuantes.append(reducao_possivel)
                calculo_detalhado += f"| Atenuante {i} | {pena_provisoria:.1f} anos | -{reducao_possivel:.1f} anos |\n"
                calculo_detalhado += f"| **LIMITE MÍNIMO** | **{min_pena:.1f} anos** | **Súmula 231** |\n"
                aplicou_sumula_231_atenuante = True
            else:
                calculo_detalhado += f"| Atenuante {i} | {pena_provisoria:.1f} anos | -0.0 anos (Limite Mínimo) |\n"
    
    # Aplicar Agravantes 
    ajustes_agravantes = []
    for i, agravante in enumerate(agravantes, 1):
        aumento = ajuste_fracao_2fase
        pena_provisoria += aumento
        ajustes_agravantes.append(aumento)
        calculo_detalhado += f"| Agravante {i} | {pena_provisoria:.1f} anos | +{aumento:.1f} anos (1/6 PB) |\n"
        
    st.markdown(f"**Pena Provisória (2ª Fase): {pena_provisoria:.1f} anos**")
    
    # 3. TERCEIRA FASE: MAJORANTES E MINORANTES
    
    # Fração de ajuste padrão (1/4 da Pena Base)
    ajuste_fracao_3fase = pena_base_ajustada * (1/4) 
    pena_definitiva = pena_provisoria
    aplicou_sumula_231_minorante = False
    
    # Aplicar Majorantes (Causas de Aumento)
    ajustes_majorantes = []
    for i, majorante in enumerate(majorantes, 1):
        aumento = ajuste_fracao_3fase
        pena_definitiva += aumento
        ajustes_majorantes.append(aumento)
        calculo_detalhado += f"| Majorante {i} | {pena_definitiva:.1f} anos | +{aumento:.1f} anos (1/4 PB) |\n"
    
    # Aplicar Minorantes (Causas de Diminuição - com LIMITE MÍNIMO LEGAL)
    ajustes_minorantes = []
    for i, minorante in enumerate(minorantes, 1):
        reducao = ajuste_fracao_3fase
        if (pena_definitiva - reducao) >= min_pena:
            pena_definitiva -= reducao
            ajustes_minorantes.append(reducao)
            calculo_detalhado += f"| Minorante {i} | {pena_definitiva:.1f} anos | -{reducao:.1f} anos (1/4 PB) |\n"
        else:
            reducao_possivel = pena_definitiva - min_pena
            if reducao_possivel > 0.05:
                pena_definitiva = min_pena
                ajustes_minorantes.append(reducao_possivel)
                calculo_detalhado += f"| Minorante {i} | {pena_definitiva:.1f} anos | -{reducao_possivel:.1f} anos |\n"
                calculo_detalhado += f"| **LIMITE MÍNIMO** | **{min_pena:.1f} anos** | **Súmula 231** |\n"
                aplicou_sumula_231_minorante = True
            else:
                calculo_detalhado += f"| Minorante {i} | {pena_definitiva:.1f} anos | -0.0 anos (Limite Mínimo) |\n"

    # 4. Ajuste Final e Limites Legais (Mínimo e Máximo)
    pena_final_bruta = pena_definitiva
    pena_final = min(max_pena, max(min_pena, pena_final_bruta)) # Aplica o teto máximo e o piso mínimo
    
    aplicou_limite_maximo = pena_final < pena_final_bruta
    aplicou_sumula_231_final = aplicou_sumula_231_atenuante or aplicou_sumula_231_minorante or (pena_final_bruta < min_pena)
    
    if aplicou_limite_maximo:
        calculo_detalhado += f"| **LIMITE MÁXIMO** | **{max_pena:.1f} anos** | **Ajuste final** |\n"
    elif aplicou_sumula_231_final:
        calculo_detalhado += f"| **LIMITE MÍNIMO** | **{min_pena:.1f} anos** | **Súmula 231** |\n"
    else:
        calculo_detalhado += f"| **PENA DEFINITIVA** | **{pena_final:.1f} anos** | **Final** |\n"
    
    st.subheader("📊 Detalhamento do Cálculo (Sistema Trifásico - Art. 68 CP)")
    st.markdown(calculo_detalhado)
    
    # Alertas sobre a Súmula 231
    if aplicou_sumula_231_final:
        st.warning("""
        **⚠️ APLICAÇÃO DA SÚMULA 231 DO STJ**
        
        *"A incidência da circunstância atenuante não pode conduzir à redução da pena abaixo do mínimo legal."*
        
        **Fundamento:** A pena foi limitada ao mínimo legal previsto para o crime, conforme jurisprudência consolidada.
        """)

    # ------------------------------------------------------------------
    ## 5️⃣ Fase 5: Tipo de Pena Privativa
    # ------------------------------------------------------------------
    
    st.header("5️⃣ Fase 5: Tipo de Pena Privativa (Reclusão ou Detenção)")
    
    tipo_pena_info = crime_info.get('Tipo_Penal_Estrutural', crime_info.get('tipo_penal', ''))
    if 'Reclusão' in str(tipo_pena_info):
        tipo_pena = "RECLUSÃO"
        cor_tipo_pena = "#ff4444"
        descricao_tipo = "Pena mais grave - Regimes: Fechado, Semiaberto ou Aberto"
    elif 'Detenção' in str(tipo_pena_info):
        tipo_pena = "DETENÇÃO"
        cor_tipo_pena = "#ffaa00"
        descricao_tipo = "Pena menos grave - Regimes: Semiaberto ou Aberto (o regime inicial fechado não é possível)"
    else:
        tipo_pena = "PENA PRIVATIVA DE LIBERDADE"
        cor_tipo_pena = "#666666"
        descricao_tipo = "Tipo de pena a ser definido conforme a natureza do crime"
    
    st.markdown(f"""
    <div style="background-color: {cor_tipo_pena}20; padding: 15px; border-radius: 10px; border-left: 5px solid {cor_tipo_pena};">
        <h3 style="color: {cor_tipo_pena}; margin: 0;">📋 TIPO DE PENA: {tipo_pena}</h3>
        <p style="margin: 5px 0 0 0;">{descricao_tipo}</p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    ## 6️⃣ Fase 6: Regime de Cumprimento
    # ------------------------------------------------------------------
    
    st.header("6️⃣ Fase 6: Regime de Cumprimento (Art. 33 CP)")
    
    reincidente = "Reincidência (Art. 61, I)" in agravantes
    
    if tipo_pena == "RECLUSÃO":
        if pena_final > 8:
            regime = "FECHADO"
            cor_regime = "#ff4444"
            descricao = "Presídio de segurança máxima/média"
            fundamento = "Art. 33, §2º, 'a' - Pena superior a 8 anos"
        elif pena_final >= 4:
            if not reincidente:
                regime = "SEMIABERTO"
                cor_regime = "#ffaa00"
                descricao = "Colônia agrícola, industrial ou similar"
                fundamento = "Art. 33, §2º, 'b' - Não reincidente, pena 4-8 anos"
            else:
                regime = "FECHADO"
                cor_regime = "#ff4444"
                descricao = "Presídio de segurança máxima/média"
                fundamento = "Art. 33, §2º - Reincidente, pena 4-8 anos, salvo circ. jud. favoráveis"
        else:
            if not reincidente:
                regime = "ABERTO"
                cor_regime = "#44cc44"
                descricao = "Casa de albergado, trabalho externo"
                fundamento = "Art. 33, §2º, 'c' - Não reincidente, pena até 4 anos"
            else:
                regime = "SEMIABERTO"
                cor_regime = "#ffaa00"
                descricao = "Colônia agrícola, industrial ou similar"
                fundamento = "Art. 33, §2º - Reincidente, pena até 4 anos, salvo circ. jud. favoráveis"
    
    else: # DETENÇÃO
        if pena_final > 4:
            regime = "SEMIABERTO"
            cor_regime = "#ffaa00"
            descricao = "Colônia agrícola, industrial ou similar"
            fundamento = "Art. 33 - Detenção: pena superior a 4 anos = semiaberto"
        else:
            regime = "ABERTO"
            cor_regime = "#44cc44"
            descricao = "Casa de albergado, trabalho externo"
            fundamento = "Art. 33 - Detenção: pena até 4 anos = aberto"
    
    st.markdown(f"""
    <div style="background-color: {cor_regime}20; padding: 20px; border-radius: 10px; border-left: 5px solid {cor_regime};">
        <h2 style="color: {cor_regime}; margin: 0;">🔒 REGIME {regime}</h2>
        <p style="margin: 10px 0 0 0; font-size: 16px;"><strong>{descricao}</strong></p>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;"><em>{fundamento}</em></p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    ## 7️⃣ Fase 7: Substituição por Pena Restritiva de Direitos
    # ------------------------------------------------------------------
    
    st.header("7️⃣ Fase 7: Substituição por Pena Restritiva de Direitos (Art. 44 CP)")
    
    pode_substituir = True
    condicoes = []
    
    # Condição I: Pena até 4 anos e crime sem violência/grave ameaça
    if pena_final <= 4:
        condicoes.append("✅ Pena não superior a 4 anos")
    else:
        condicoes.append("❌ Pena superior a 4 anos")
        pode_substituir = False
    
    crimes_violentos = ["homicídio", "lesão corporal", "latrocínio", "estupro", "roubo", "sequestro", "extorsão"]
    crime_violento = any(violento in crime_info['descricao_completa'].lower() for violento in crimes_violentos)
    
    if not crime_violento:
        condicoes.append("✅ Crime sem violência ou grave ameaça")
    else:
        condicoes.append("❌ Crime com violência ou grave ameaça")
        pode_substituir = False
    
    # Condição II: Não reincidente em crime doloso
    if not reincidente:
        condicoes.append("✅ Réu não reincidente")
    else:
        if crime_violento:
             condicoes.append("❌ Réu reincidente e crime violento")
             pode_substituir = False
        else:
             condicoes.append("⚠️ Réu reincidente: Juiz pode analisar aplicação excepcional (Art. 44, §3º)")
    
    # Condição III: Análise do Art. 59
    if circunstancia == 0:
        condicoes.append("✅ Circunstâncias judiciais favoráveis (Art. 59)")
    else:
        condicoes.append("⚠️ Circunstâncias judiciais desfavoráveis (Juiz deve analisar a suficiência da PRD)")

    if pode_substituir:
        substituicao = "**CABE SUBSTITUIÇÃO** por pena restritiva de direitos (PRD)"
        cor_subst = "#44cc44"
        fundamento_subst = "Art. 44 CP - Preenchidos os requisitos legais básicos"
    else:
        substituicao = "**NÃO CABE SUBSTITUIÇÃO**"
        cor_subst = "#ff4444"
        fundamento_subst = "Art. 44 CP - Não preenchidos os requisitos legais básicos (Ex: Pena > 4 anos ou Crime Violento)"
    
    st.markdown(f"""
    <div style="background-color: {cor_subst}20; padding: 15px; border-radius: 10px; border-left: 5px solid {cor_subst};">
        <h3 style="color: {cor_subst}; margin: 0;">{substituicao}</h3>
        <p style="margin: 5px 0 0 0;">{fundamento_subst}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("**📝 Condições analisadas para substituição:**")
    for condicao in condicoes:
        st.write(condicao)

    # ------------------------------------------------------------------
    ## 📊 Visualização da Dosimetria
    # ------------------------------------------------------------------

    st.header("📊 Visualização da Dosimetria")
    st.subheader("🎯 Composição da Pena Final (Waterfall)")
    
    data = [
        go.Waterfall(
            name = "Dosimetria",
            orientation = "v",
            measure = ["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
            x = [
                "Pena Mínima (Base)", 
                "1ª Fase (Circunstâncias)", 
                "2ª Fase (Atenuantes)", 
                "2ª Fase (Agravantes)",
                "3ª Fase (Minorantes)",
                "3ª Fase (Majorantes)",
                "Pena Final",
            ],
            textposition = "outside",
            text = [
                f"{min_pena:.1f}", 
                f"{ajuste_circunstancia:+.1f}", 
                f"{-sum(ajustes_atenuantes):.1f}", 
                f"{sum(ajustes_agravantes):+.1f}",
                f"{-sum(ajustes_minorantes):.1f}",
                f"{sum(ajustes_majorantes):+.1f}",
                f"{pena_final:.1f}"
            ],
            y = [
                min_pena, 
                ajuste_circunstancia, 
                -sum(ajustes_atenuantes), 
                sum(ajustes_agravantes),
                -sum(ajustes_minorantes),
                sum(ajustes_majorantes),
                pena_final 
            ],
            connector = {"line": {"color": "rgb(63, 63, 63)"}},
            increasing = {"marker":{"color":"#FF9800"}},
            decreasing = {"marker":{"color":"#4CAF50"}},
            totals = {"marker":{"color":"#2196F3"}}
        )
    ]

    fig_composicao = go.Figure(data=data)
    
    fig_composicao.update_layout(
        title = "Impacto dos Componentes no Cálculo da Pena",
        showlegend = False,
        height=550,
        plot_bgcolor='rgba(240,240,240,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    fig_composicao.add_hline(y=max_pena, line_dash="dash", line_color="#F44336", 
                             annotation_text=f"Máximo Legal: {max_pena:.1f} anos",
                             annotation_position="top left")
                             
    fig_composicao.add_hline(y=min_pena, line_dash="dash", line_color="#2196F3", 
                             annotation_text=f"Mínimo Legal: {min_pena:.1f} anos",
                             annotation_position="bottom left")
    
    st.plotly_chart(fig_composicao, use_container_width=True)

    # Resumo final estilizado
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin: 20px 0; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.2);">
        <h3 style="color: white; margin: 0 0 15px 0; font-weight: 600;">🎯 RESUMO FINAL DA DOSIMETRIA</h3>
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px; min-width: 200px;">
                <div style="font-weight: bold; color: #333; font-size: 16px;">Pena Final</div>
                <div style="font-size: 24px; font-weight: bold; color: #2196F3;">{pena_final:.1f} anos</div>
            </div>
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px; min-width: 200px;">
                <div style="font-weight: bold; color: #333; font-size: 16px;">Tipo de Pena</div>
                <div style="font-size: 16px; font-weight: bold; color: {cor_tipo_pena};">{tipo_pena}</div>
            </div>
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px; min-width: 200px;">
                <div style="font-weight: bold; color: #333; font-size: 16px;">Regime</div>
                <div style="font-size: 16px; font-weight: bold; color: {cor_regime};">{regime}</div>
            </div>
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px; min-width: 200px;">
                <div style="font-weight: bold; color: #333; font-size: 16px;">Substituição</div>
                <div style="font-size: 14px; font-weight: bold; color: {cor_subst};">{substituicao.replace('**', '')}</div>
            </div>
        </div>
        {"<div style='background: rgba(255,255,255,0.9); padding: 10px; border-radius: 10px; margin: 10px;'><div style='font-weight: bold; color: #ff4444;'>⚠️ APLICADA SÚMULA 231 - PENA LIMITADA AO MÍNIMO LEGAL</div></div>" if aplicou_sumula_231_final else ""}
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------
## 📚 Referências Legais Completas
# ------------------------------------------------------------------

st.header("📚 Referências Legais Completas")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Agravantes/Atenuantes", "⚖️ Penas Restritivas", "🔍 Súmulas", "📊 Progressão"])

with tab1:
    col_ref1, col_ref2 = st.columns(2)
    
    with col_ref1:
        st.subheader("Agravantes (Art. 61-62 CP)")
        st.write("""
        **Art. 61 - Agravantes sempre aplicáveis:**
        - Reincidência (Art. 61, I)
        - Motivo fútil ou torpe
        - Traição, emboscada, dissimulação
        - Emprego de veneno, fogo, explosivo, tortura
        - Meio insidioso ou cruel
        - Crime contra família
        - Abuso de autoridade/poder
        - Contra criança/idoso/enfermo/grávida
        - Embriaguez preordenada
        - Em instituição de ensino
        
        **Art. 62 - Agravantes no concurso:**
        - Promotor/organizador do crime
        - Coação/indução à execução
        - Instigação a pessoa sob autoridade
        - Execução mediante paga
        """)
    
    with col_ref2:
        st.subheader("Atenuantes (Art. 65-66 CP)")
        st.write("""
        **Art. 65 - Atenuantes sempre aplicáveis:**
        - Menor de 21 anos na data do fato
        - Maior de 70 anos na sentença
        - Desconhecimento da lei
        - Motivo de relevante valor social/moral
        - Arrependimento eficiente
        - Reparação do dano
        - Coação resistível
        - Ordem superior
        - Violenta emoção por ato injusto
        - Confissão espontânea (Súmula 545 STJ)
        - Influência de multidão
        
        **Art. 66 - Atenuantes genéricas:**
        - Circunstância relevante não prevista
        """)

with tab2:
    st.subheader("Arts. 43-48 CP - Penas Restritivas de Direitos")
    st.write("""
    **Art. 43 - Espécies:**
    - 💰 Prestação pecuniária
    - 📉 Perda de bens e valores  
    - 🏛️ Prestação de serviços à comunidade
    - 🚫 Interdição temporária de direitos
    - 🎯 Limitação de fim de semana
    
    **Art. 44 - Requisitos para substituição:**
    - Pena ≤ 4 anos + crime sem violência/grave ameaça
    - Não reincidente em crime doloso (salvo Art. 44, §3º)
    - Análise favorável do Art. 59
    """)

with tab3:
    st.subheader("Súmulas Relevantes")
    st.write("""
    **Súmula 231 STJ (IMPORTANTE):**
    - *"A incidência da circunstância atenuante não pode conduzir à redução da pena abaixo do mínimo legal."*
    - Efeito: Impede que atenuantes (2ª Fase) ou minorantes (3ª Fase) reduzam a pena abaixo do patamar mínimo estabelecido em lei
    
    **Súmula 444 STJ:**
    - A dosimetria da pena deve observar o sistema trifásico do Art. 68 CP
    - O juiz deve fundamentar cada fase do cálculo
    
    **Súmula 545 STJ:**
    - *"Quando a confissão for utilizada para a formação do convencimento do julgador, o réu fará jus à atenuante prevista no art. 65, III, d, do Código Penal."*
    """)

with tab4:
    st.subheader("Progressão de Regime (Lei de Execução Penal)")
    st.write("""
    **Requisitos para Progressão (LEP Art. 112):**
    - Bom comportamento carcerário (atestado pelo diretor)
    - Cumprimento de **fração da pena no regime anterior**:
        - **16%** se primário e crime sem violência/grave ameaça.
        - **20%** se reincidente e crime sem violência/grave ameaça.
        - **25%** se primário e crime com violência/grave ameaça.
        - **30%** se reincidente e crime com violência/grave ameaça.
        - **40%** se crime hediondo ou equiparado, se primário.
        - **50%** se crime hediondo ou equiparado, se reincidente.
        - **60%** se crime hediondo/equiparado e resultar em morte, se primário.
        - **70%** se crime hediondo/equiparado e resultar em morte, se reincidente.
    """)

st.markdown("---")
st.write("**⚖️ Ferramenta educacional - Consulte sempre a legislação atual e um profissional do direito**")
st.write("**📚 Base legal:** Arts. 33, 43-48, 59, 61, 65, 68 do Código Penal Brasileiro e Lei nº 7.210/84 (LEP)")
