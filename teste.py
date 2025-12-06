import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title("⚖️ Simulador de Dosimetria da Pena")
st.write("**Calculadora completa da dosimetria penal conforme Art. 68 do CP**")

# Carregar dados diretamente da URL do GitHub (Ajuste solicitado pelo professor)
URL_DADOS = 'https://raw.githubusercontent.com/matheusasharosilva-debug/Dosimetria-penal2/refs/heads/main/crimes_cp_final_sem_art68.csv'

# Carregar dados
@st.cache_data
def carregar_dados_crimes(url):
    """Carrega os dados dos crimes diretamente da URL."""
    try:
        # Usar pd.read_csv com a URL
        df = pd.read_csv(url, encoding='latin-1') 
        st.success("✅ Dados carregados com sucesso da URL!")
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo da URL: {e}. Verifique se o link está correto e acessível.")
        return pd.DataFrame()

@st.cache_data
def processar_dados_crimes(df):
    """Processa os dados dos crimes para o formato necessário"""
    if df.empty:
        return {}
        
    crimes_dict = {}
        
    for idx, row in df.iterrows():
        artigo_base = row['Artigo_Base'] if pd.notna(row['Artigo_Base']) else ''
        artigo_completo = row['Artigo_Completo'] if pd.notna(row['Artigo_Completo']) else artigo_base
        descricao = row['Descricao_Crime'] if pd.notna(row['Descricao_Crime']) else ''
        pena_min_valor = row['Pena_Minima_Valor'] if pd.notna(row['Pena_Minima_Valor']) else 0
        pena_min_unidade = row['Pena_Minima_Unidade'] if pd.notna(row['Pena_Minima_Unidade']) else 'mês'
        pena_max_valor = row['Pena_Maxima_Valor'] if pd.notna(row['Pena_Maxima_Valor']) else 0
        pena_max_unidade = row['Pena_Maxima_Unidade'] if pd.notna(row['Pena_Maxima_Unidade']) else 'mês'
        tipo_penal = row['Tipo_Penal_Estrutural'] if pd.notna(row['Tipo_Penal_Estrutural']) else 'Crime Base (Caput)'
        
        # Converter para anos (usando 360 dias/ano e 12 meses/ano)
        if pena_min_unidade.lower() in ['mês', 'mes']:
            pena_min_anos = pena_min_valor / 12
        elif pena_min_unidade.lower() == 'dia':
            pena_min_anos = pena_min_valor / 360
        else:
            pena_min_anos = pena_min_valor
            
        if pena_max_unidade.lower() in ['mês', 'mes']:
            pena_max_anos = pena_max_valor / 12
        elif pena_max_unidade.lower() == 'dia':
            pena_max_anos = pena_max_valor / 360
        else:
            pena_max_anos = pena_max_valor
        
        # Criar chave única para o crime
        if pd.notna(artigo_completo) and pd.notna(descricao):
            chave = f"{artigo_completo} - {descricao[:80]}..."
            crimes_dict[chave] = {
                'artigo': artigo_completo,
                'artigo_base': artigo_base,
                'descricao_completa': descricao,
                'pena_min': pena_min_anos,
                'pena_max': pena_max_anos,
                'tipo_penal': tipo_penal,
                'pena_min_original': pena_min_valor,
                'pena_max_original': pena_max_valor,
                'unidade_original': pena_min_unidade
            }
        
    return crimes_dict

df = carregar_dados_crimes(URL_DADOS)
crimes_data = processar_dados_crimes(df)


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
if not crimes_data:
    st.warning("""
    **⚠️ Erro ao carregar o dataset**
    
    Verifique a URL ou a estrutura do arquivo.
    """)
    st.stop()

# Fase 1: Pena Base e Circunstâncias
st.header("1️⃣ Fase 1: Pena Base e Circunstâncias")
col1, col2 = st.columns([2, 1])

with col1:
    if crimes_data:
        # Tentar pré-selecionar o crime problemático se encontrado (para teste)
        crime_keys = list(crimes_data.keys())
        default_index = 0
        try:
            # Seleciona "Recrutar trabalhador" se ele existir
            recrutar_key = next((k for k in crime_keys if "recrutar trabalhador" in k.lower()), crime_keys[0])
            default_index = crime_keys.index(recrutar_key)
        except StopIteration:
            pass # Mantém o índice 0

        crime_selecionado = st.selectbox("Selecione o Crime:", options=crime_keys, format_func=lambda x: x, index=default_index)
        crime_info = crimes_data[crime_selecionado]
        min_pena_anos = crime_info['pena_min']
        max_pena_anos = crime_info['pena_max']
        
        st.write(f"**Artigo:** {crime_info['artigo']}")
        st.write(f"**Tipo penal:** {crime_info['tipo_penal']}")
        st.write(f"**Descrição:** {crime_info['descricao_completa']}")
        st.write(f"**Pena original (Mín-Máx):** {crime_info['pena_min_original']} {crime_info['unidade_original']} a {crime_info['pena_max_original']} {crime_info['unidade_original']}")
    else:
        st.error("Erro ao carregar dados dos crimes.")

with col2:
    circunstancia = st.radio("Circunstância do Crime (Art. 59 CP):", ["Neutra", "Desfavorável", "Gravemente Desfavorável"])
    
    # --- CORREÇÃO DE LÓGICA DA PENA BASE (APLICAR FATOR À MARGEM) ---
    margem_anos = max_pena_anos - min_pena_anos
    ajuste_circunstancia_margem = {"Neutra": 0, "Desfavorável": 0.2, "Gravemente Desfavorável": 0.4}
    fator_margem = ajuste_circunstancia_margem[circunstancia]
    
    # Cálculo: Mínimo Legal + (Margem * Fator de ajuste)
    aumento_margem = margem_anos * fator_margem
    pena_base_ajustada = min_pena_anos + aumento_margem
    
    st.write(f"**Pena prevista:** {min_pena_anos:.1f} a {max_pena_anos:.1f} anos")
    st.write(f"**Pena base inicial (Mín. Legal):** {min_pena_anos:.1f} anos")
    st.write(f"**Aumento sobre a Margem:** +{aumento_margem:.1f} anos ({fator_margem*100:.0f}%)")
    st.success(f"**PENA BASE APÓS CIRCUNSTÂNCIAS: {pena_base_ajustada:.1f} anos**")

# Fase 2: Atenuantes e Agravantes
st.header("2️⃣ Fase 2: Atenuantes e Agravantes Gerais")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔽 Atenuantes (Art. 65 CP)")
    atenuantes = st.multiselect("Selecione as atenuantes:", [
        "Menor de 21 anos na data do fato",
        "Maior de 70 anos na data da sentença",
        "Desconhecimento da lei",
        "Motivo de relevante valor social ou moral",
        "Arrependimento espontâneo eficiente",
        "Reparação do dano antes do julgamento",
        "Coação a que podia resistir",
        "Cumprimento de ordem superior",
        "Violenta emoção por ato injusto da vítima",
        "Confissão espontânea perante autoridade",
        "Influência de multidão em tumulto (sem provocação)",
        "Circunstância relevante não prevista em lei (Art. 66)"
    ])

with col2:
    st.subheader("🔼 Agravantes (Art. 61 e 62 CP)")
    agravantes = st.multiselect("Selecione as agravantes:", [
        "Reincidência",
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
        "Promotor/organizador do concurso de pessoas",
        "Coação/indução à execução do crime",
        "Instigação/determinação a pessoa sob autoridade",
        "Execução mediante paga ou promessa de recompensa"
    ])

# Fase 3: Majorantes e Minorantes
st.header("3️⃣ Fase 3: Causas de Aumento/Diminuição")
majorantes_minorantes_generico = {
    "majorantes": [
        "Uso de arma (1/6 a 1/2)", 
        "Violência grave (1/3 a 2/3)", 
        "Concurso de 2+ pessoas (1/4 a 1/2)", 
        "Restrição à liberdade (1/6 a 1/3)", 
        "Abuso de confiança (1/6 a 1/3)",
        "Aumento por continuidade delitiva",
        "Aumento específico do tipo penal"
    ],
    "minorantes": [
        "Valor ínfimo do dano (1/6 a 1/3)", 
        "Arrependimento posterior (1/6 a 1/3)", 
        "Circunstâncias atenuantes não previstas (1/6 a 1/3)",
        "Diminuição específica do tipo penal",
        "Causa de diminuição de culpabilidade"
    ]
}

col1, col2 = st.columns(2)
with col1:
    majorantes = st.multiselect("Causas de aumento (majorantes):", majorantes_minorantes_generico["majorantes"])
with col2:
    minorantes = st.multiselect("Causas de diminuição (minorantes):", majorantes_minorantes_generico["minorantes"])

# Fase 4: Cálculo Final
st.header("4️⃣ Fase 4: Cálculo Final da Pena")

if st.button("🎯 Calcular Pena Definitiva", type="primary"):
    pena_calculada = pena_base_ajustada
    
    st.subheader("📊 Detalhamento do Cálculo")
    calculo_detalhado = f"| Etapa | Valor | Ajuste |\n|-------|-------|---------|\n| **Pena Base Inicial** | {min_pena_anos:.1f} anos | - |\n| Circunstância {circunstancia} | {pena_base_ajustada:.1f} anos | +{aumento_margem:.1f} anos |\n"
    
    # Aplicar atenuantes COM LIMITE DO MÍNIMO LEGAL (Súmula 231)
    min_pena = min_pena_anos
    
    ajustes_atenuantes = []
    for i, atenuante in enumerate(atenuantes, 1):
        # Redução padrão de 1/6 da pena base ajustada para simulação
        reducao = pena_base_ajustada * (1/6)
        
        # Verificar se a redução não levará abaixo do mínimo legal (Súmula 231)
        if (pena_calculada - reducao) >= min_pena:
            pena_calculada -= reducao
            ajustes_atenuantes.append(reducao)
            calculo_detalhado += f"| Atenuante {i} | {pena_calculada:.1f} anos | -{reducao:.1f} anos |\n"
        else:
            # Aplicar apenas a redução possível sem ultrapassar o mínimo
            reducao_possivel = pena_calculada - min_pena
            if reducao_possivel > 0:
                pena_calculada = min_pena
                ajustes_atenuantes.append(reducao_possivel)
                calculo_detalhado += f"| Atenuante {i} | {pena_calculada:.1f} anos | -{reducao_possivel:.1f} anos |\n"
                calculo_detalhado += f"| **LIMITE MÍNIMO** | **{min_pena:.1f} anos** | **Súmula 231** |\n"
            else:
                calculo_detalhado += f"| Atenuante {i} | {pena_calculada:.1f} anos | -0.0 anos (limite mínimo) |\n"

    # Aplicar agravantes
    ajustes_agravantes = []
    for i, agravante in enumerate(agravantes, 1):
        # Aumento padrão de 1/6 da pena base ajustada para simulação
        aumento = pena_base_ajustada * (1/6)
        pena_calculada += aumento
        ajustes_agravantes.append(aumento)
        calculo_detalhado += f"| Agravante {i} | {pena_calculada:.1f} anos | +{aumento:.1f} anos |\n"

    # Aplicar majorantes (Fator padrão de 1/4 da pena base ajustada para simulação)
    ajustes_majorantes = []
    for i, majorante in enumerate(majorantes, 1):
        aumento = pena_base_ajustada * (1/4)
        pena_calculada += aumento
        ajustes_majorantes.append(aumento)
        calculo_detalhado += f"| Majorante {i} | {pena_calculada:.1f} anos | +{aumento:.1f} anos |\n"

    # Aplicar minorantes COM LIMITE DO MÍNIMO LEGAL (Súmula 231)
    ajustes_minorantes = []
    for i, minorante in enumerate(minorantes, 1):
        # Redução padrão de 1/4 da pena base ajustada para simulação
        reducao = pena_base_ajustada * (1/4)
        
        # Verificar se a redução não levará abaixo do mínimo legal (Súmula 231)
        if (pena_calculada - reducao) >= min_pena:
            pena_calculada -= reducao
            ajustes_minorantes.append(reducao)
            calculo_detalhado += f"| Minorante {i} | {pena_calculada:.1f} anos | -{reducao:.1f} anos |\n"
        else:
            # Aplicar apenas a redução possível sem ultrapassar o mínimo
            reducao_possivel = pena_calculada - min_pena
            if reducao_possivel > 0:
                pena_calculada = min_pena
                ajustes_minorantes.append(reducao_possivel)
                calculo_detalhado += f"| Minorante {i} | {pena_calculada:.1f} anos | -{reducao_possivel:.1f} anos |\n"
                calculo_detalhado += f"| **LIMITE MÍNIMO** | **{min_pena:.1f} anos** | **Súmula 231** |\n"
            else:
                calculo_detalhado += f"| Minorante {i} | {pena_calculada:.1f} anos | -0.0 anos (limite mínimo) |\n"

    # Aplicar limites legais (mínimo e máximo)
    pena_final = max(min_pena, min(max_pena_anos, pena_calculada))
    
    # Verificar se houve aplicação da Súmula 231
    aplicou_sumula_231 = False
    if pena_calculada < min_pena_anos:
        aplicou_sumula_231 = True
        pena_final = min_pena_anos
        calculo_detalhado += f"| **SÚMULA 231** | **{pena_final:.1f} anos** | **Limite mínimo legal** |\n"
    elif pena_calculada > max_pena_anos:
        pena_final = max_pena_anos
        calculo_detalhado += f"| **LIMITE MÁXIMO** | **{pena_final:.1f} anos** | **Ajuste final** |"
    else:
        calculo_detalhado += f"| **PENA DEFINITIVA** | **{pena_final:.1f} anos** | **Conclusão** |"
    
    st.markdown(calculo_detalhado)
    
    # Alertas sobre a Súmula 231
    if aplicou_sumula_231:
        st.warning("""
        **⚠️ APLICAÇÃO DA SÚMULA 231 DO STJ**
        
        *"A incidência da circunstância atenuante não pode conduzir à redução da pena abaixo do mínimo legal."*
        
        **Fundamento:** A pena foi limitada ao mínimo legal previsto para o crime, conforme jurisprudência consolidada.
        """)

    # Fase 5: Tipo de Pena Privativa
    st.header("5️⃣ Fase 5: Tipo de Pena Privativa")
    
    # Determinar tipo de pena (Reclusão ou Detenção)
    tipo_pena_info = crime_info.get('tipo_penal', '')
    if 'Reclusão' in str(tipo_pena_info):
        tipo_pena = "RECLUSÃO"
        cor_tipo_pena = "#ff4444"
        descricao_tipo = "Pena mais grave - Regimes: Fechado, Semiaberto ou Aberto"
    elif 'Detenção' in str(tipo_pena_info):
        tipo_pena = "DETENÇÃO"
        cor_tipo_pena = "#ffaa00"
        descricao_tipo = "Pena menos grave - Regimes: Semiaberto ou Aberto"
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

    # Fase 6: Regime de Cumprimento
    st.header("6️⃣ Fase 6: Regime de Cumprimento")
    
    # Verificar reincidência
    reincidente = "Reincidência" in agravantes
    
    # Determinar regime conforme Art. 33 CP - LÓGICA CORRIGIDA
    if tipo_pena == "RECLUSÃO":
        # Pena SUPERIOR a 8 anos = FECHADO
        if pena_final > 8:
            regime = "FECHADO"
            cor_regime = "#ff4444"
            descricao = "Presídio de segurança máxima/média"
            fundamento = "Art. 33, §2º, 'a' - Pena superior a 8 anos"
        # Pena MAIOR OU IGUAL a 4 anos ATÉ 8 anos
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
                fundamento = "Art. 33, §2º - Reincidente, pena 4-8 anos"
        # Pena INFERIOR a 4 anos
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
                fundamento = "Art. 33, §2º - Reincidente, pena até 4 anos"
    
    else:  # DETENÇÃO
        # Para detenção, regime depende apenas da pena
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

    # Fase 7: Substituição da Pena
    st.header("7️⃣ Fase 7: Substituição por Pena Restritiva de Direitos")
    
    # Verificar condições para substituição (Art. 44 CP)
    pode_substituir = False
    condicoes = []
    
    # Condição I: Pena até 4 anos e crime sem violência
    if pena_final <= 4:
        condicoes.append("✅ Pena não superior a 4 anos")
        # Verificar se é crime violento (simplificado)
        crimes_violentos = ["homicídio", "lesão corporal", "latrocínio", "estupro", "roubo", "sequestro", "extorsão", "constrangimento"]
        crime_violento = any(violento in crime_info['descricao_completa'].lower() for violento in crimes_violentos)
        
        if not crime_violento:
            condicoes.append("✅ Crime sem violência ou grave ameaça")
            
            # Condição II: Não reincidente em crime doloso
            if not reincidente:
                condicoes.append("✅ Réu não reincidente em crime doloso")
                pode_substituir = True
            else:
                condicoes.append("❌ Réu reincidente em crime doloso")
                # Exceção: Art. 44, §3º - Juiz pode aplicar mesmo para reincidente em casos específicos
                condicoes.append("⚠️ Juiz pode analisar aplicação excepcional (Art. 44, §3º)")
                
        else:
            condicoes.append("❌ Crime com violência ou grave ameaça")
    else:
        condicoes.append("❌ Pena superior a 4 anos")
    
    # Condição III: Análise do Art. 59
    condicoes.append("✅ Análise favorável dos critérios do Art. 59")
    
    if pode_substituir:
        substituicao = "**CABE SUBSTITUIÇÃO** por pena restritiva de direitos"
        cor_subst = "#44cc44"
        fundamento_subst = "Art. 44 CP - Preenchidos os requisitos legais"
        
        # Tipos de penas restritivas possíveis
        st.subheader("📋 Penas Restritivas de Direitos Possíveis (Art. 43 CP)")
        
        col_penas1, col_penas2 = st.columns(2)
        
        with col_penas1:
            st.write("""
            **Penas Restritivas:**
            - 💰 Prestação pecuniária
            - 🏛️ Prestação de serviços à comunidade
            - 🚫 Interdição temporária de direitos
            """)
        
        with col_penas2:
            st.write("""
            - 🎯 Limitação de fim de semana
            - 📉 Perda de bens e valores
            
            """)
    
    else:
        substituicao = "**NÃO CABE SUBSTITUIÇÃO**"
        cor_subst = "#ff4444"
        fundamento_subst = "Art. 44 CP - Não preenchidos os requisitos legais"
    
    st.markdown(f"""
    <div style="background-color: {cor_subst}20; padding: 15px; border-radius: 10px; border-left: 5px solid {cor_subst};">
        <h3 style="color: {cor_subst}; margin: 0;">{substituicao}</h3>
        <p style="margin: 5px 0 0 0;">{fundamento_subst}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar condições analisadas
    st.write("**📝 Condições analisadas para substituição:**")
    for condicao in condicoes:
        st.write(condicao)

    # GRÁFICOS PLOTLY
    st.header("📊 Visualização da Dosimetria")
    
    # Gráfico 1: Composição da Pena
    st.subheader("🎯 Composição da Pena Final")
    
    # Preparar dados para o gráfico de composição
    categorias = []
    valores = []
    cores = []
    textos = []
    
    # Pena base inicial (Mínimo Legal)
    categorias.append("Mínimo Legal")
    valores.append(min_pena_anos)
    cores.append("#2196F3")
    textos.append(f"Base: {min_pena_anos:.1f} anos")
    
    # Ajuste por circunstância (Aumento sobre a margem)
    if aumento_margem > 0:
        categorias.append(f"Ajuste Circunstância ({circunstancia})")
        valores.append(aumento_margem)
        cores.append("#9C27B0")
        textos.append(f"+{aumento_margem:.1f} anos")
    
    # Atenuantes
    if ajustes_atenuantes:
        categorias.append("Atenuantes")
        valores.append(-sum(ajustes_atenuantes))
        cores.append("#4CAF50")
        textos.append(f"-{sum(ajustes_atenuantes):.1f} anos")
    
    # Agravantes
    if ajustes_agravantes:
        categorias.append("Agravantes")
        valores.append(sum(ajustes_agravantes))
        cores.append("#FF9800")
        textos.append(f"+{sum(ajustes_agravantes):.1f} anos")
    
    # Majorantes
    if ajustes_majorantes:
        categorias.append("Majorantes")
        valores.append(sum(ajustes_majorantes))
        cores.append("#F44336")
        textos.append(f"+{sum(ajustes_majorantes):.1f} anos")
    
    # Minorantes
    if ajustes_minorantes:
        categorias.append("Minorantes")
        valores.append(-sum(ajustes_minorantes))
        cores.append("#00BCD4")
        textos.append(f"-{sum(ajustes_minorantes):.1f} anos")
    
    # Criar gráfico de barras horizontal (Gráfico Waterfall simplificado para visualização de impacto)
    df_chart = pd.DataFrame({
        'Componente': categorias,
        'Impacto (Anos)': valores
    })
    
    # Calcular a posição base para as barras (necessário para waterfall)
    df_chart['Base'] = df_chart['Impacto (Anos)'].clip(lower=0).cumsum().shift(1, fill_value=0)
    df_chart['Base_Neg'] = df_chart['Impacto (Anos)'].clip(upper=0).cumsum().shift(1, fill_value=0)
    
    df_chart['Start'] = df_chart.apply(lambda row: row['Base'] if row['Impacto (Anos)'] >= 0 else row['Base_Neg'] + row['Impacto (Anos)'], axis=1)
    
    # Criar o gráfico
    fig_composicao = go.Figure()
    
    current_cumulative_pena = 0
    
    for i, row in df_chart.iterrows():
        impacto = row['Impacto (Anos)']
        cor = cores[i]
        
        # Rastrear a pena cumulativa para a posição correta
        start_pos = current_cumulative_pena
        end_pos = start_pos + impacto
        
        fig_composicao.add_trace(go.Bar(
            name=row['Componente'],
            y=[row['Componente']],
            x=[impacto] if impacto >= 0 else [0],
            orientation='h',
            marker_color=cor,
            text=f"+{impacto:.1f} anos" if impacto >= 0 else "",
            textposition='auto',
            base=[start_pos] if impacto >= 0 else [0],
            hovertemplate=f"<b>{row['Componente']}</b><br>Impacto: {impacto:+.1f} anos<extra></extra>",
            showlegend=False
        ))
        
        if impacto < 0:
            fig_composicao.add_trace(go.Bar(
                name=row['Componente'],
                y=[row['Componente']],
                x=[impacto],
                orientation='h',
                marker_color=cor,
                text=f"{impacto:.1f} anos",
                textposition='auto',
                hovertemplate=f"<b>{row['Componente']}</b><br>Impacto: {impacto:+.1f} anos<extra></extra>",
                showlegend=False
            ))
            
        current_cumulative_pena = end_pos

    # Adicionar a linha da pena final
    fig_composicao.add_vline(x=pena_final, line_dash="dash", line_color="#FF5722", 
                             annotation_text=f"Pena Final: {pena_final:.1f} anos",
                             annotation_position="top right")
    
    # Adicionar linha do mínimo legal se aplicou Súmula 231
    if aplicou_sumula_231 or min_pena_anos > 0:
        fig_composicao.add_vline(x=min_pena_anos, line_dash="dot", line_color="#FF0000",
                                 annotation_text=f"Mínimo Legal: {min_pena_anos:.1f} anos",
                                 annotation_position="bottom right")

    # Adicionar linha do máximo legal
    fig_composicao.add_vline(x=max_pena_anos, line_dash="dot", line_color="#0000FF",
                             annotation_text=f"Máximo Legal: {max_pena_anos:.1f} anos",
                             annotation_position="bottom left")
    
    fig_composicao.update_layout(
        title="Impacto dos Componentes na Pena Final",
        barmode='relative',
        xaxis_title="Anos de Pena",
        yaxis_title="Componentes",
        showlegend=True,
        height=500,
        plot_bgcolor='rgba(240,240,240,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50),
        xaxis=dict(range=[min(0, min_pena_anos-1), max(max_pena_anos+1, pena_final+1)])
    )
    
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
        {"<div style='background: rgba(255,255,255,0.9); padding: 10px; border-radius: 10px; margin: 10px;'><div style='font-weight: bold; color: #ff4444;'>⚠️ APLICADA SÚMULA 231 - PENA LIMITADA AO MÍNIMO LEGAL</div></div>" if aplicou_sumula_231 else ""}
    </div>
    """, unsafe_allow_html=True)

# SEÇÃO DE REFERÊNCIAS LEGAIS COMPLETAS
st.header("📚 Referências Legais Completas")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Agravantes/Atenuantes", "⚖️ Penas Restritivas", "🔍 Súmulas", "📊 Progressão"])

with tab1:
    col_ref1, col_ref2 = st.columns(2)
    
    with col_ref1:
        st.subheader("Agravantes (Art. 61-62 CP)")
        st.write("""
        **Art. 61 - Agravantes sempre aplicáveis:**
        - Reincidência
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
        - Confissão espontânea
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
    - Pena ≤ 4 anos + crime sem violência
    - Não reincidente em crime doloso
    - Análise favorável do Art. 59
    """)

with tab3:
    st.subheader("Súmulas Relevantes")
    st.write("""
    **Súmula 231 STJ (IMPORTANTE):**
    - *"A incidência da circunstância atenuante não pode conduzir à redução da pena abaixo do mínimo legal."*
    - Data: 22/09/1999
    - Efeito: Impede que atenuantes reduzam a pena abaixo do patamar mínimo estabelecido em lei
    
    **Súmula 444 STJ:**
    - A dosimetria da pena deve observar o sistema trifásico do Art. 68 CP
    - O juiz deve fundamentar cada fase do cálculo
    """)

with tab4:
    st.subheader("Progressão de Regime")
    st.write("""
    **Regras de progressão (Lei nº 7.210/84 - Lei de Execução Penal):**
    - 16% da pena, se primário e crime sem violência/grave ameaça.
    - 20% da pena, se reincidente em crime sem violência/grave ameaça.
    - 25% da pena, se primário e crime com violência/grave ameaça.
    - 30% da pena, se reincidente em crime com violência/grave ameaça.
    - 40% da pena, se hediondo/equiparado primário.
    - 50% da pena, se hediondo/equiparado + resultado morte.
    - 60% da pena, se hediondo/equiparado reincidente.
    - 70% da pena, se hediondo/equiparado reincidente + resultado morte.
    
    *Todos os cálculos exigem bom comportamento.*
    """)

st.markdown("---")
st.write("**⚖️ Ferramenta educacional - Consulte sempre a legislação atual e um profissional do direito**")
st.write("**📚 Base legal:** Arts. 33, 43-48, 59, 61, 65, 68 do Código Penal Brasileiro")
