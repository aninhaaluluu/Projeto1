
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time

st.set_page_config(layout="wide")
st.title("⚖️ Simulador de Dosimetria da Pena (Versão 2.0) ⚖️")
st.write("**Calculadora completa da dosimetria penal conforme Art. 68 do CP**")

# --- Constante para a URL do arquivo CSV ---
CSV_URL = 'https://gist.githubusercontent.com/aninhaaluluu/948f509c1ef9a4bb3f2128ed4f51fe60/raw/33cf2e2b33fa54807617c398c385624f5af6ad20/gistfile1.txt'
# ------------------------------------------

@st.cache_data
def processar_dados_crimes(df):
    """
    Processa os dados dos crimes, CONVERTE TODAS AS PENAS PARA ANOS 
    e trata erros de tipo de dados.
    """
    if df.empty:
        return {}, 0, 0
        
    crimes_dict = {}
    processados = 0
    pulados = 0
    art206_debug = []
    
    for idx, row in df.iterrows():
        
        # 1. DEFINIÇÃO DAS VARIÁVEIS DE TEXTO
        artigo_base = row.get('Artigo_Base', '') if pd.notna(row.get('Artigo_Base')) else ''
        artigo_completo = row.get('Artigo_Completo', '') if pd.notna(row.get('Artigo_Completo')) else artigo_base
        descricao = row.get('Descricao_Crime', '') if pd.notna(row.get('Descricao_Crime')) else ''
        tipo_penal = row.get('Tipo_Penal_Estrutural', 'Crime Base (Caput)') if pd.notna(row.get('Tipo_Penal_Estrutural')) else 'Crime Base (Caput)'
        
        # 🔥 DEBUG ESPECIAL PARA ART. 206
        if '206' in str(artigo_completo) or '206' in str(artigo_base):
            art206_debug.append({
                'linha': idx,
                'artigo_completo': artigo_completo,
                'artigo_base': artigo_base,
                'pena_min': row.get('Pena_Minima_Valor'),
                'pena_max': row.get('Pena_Maxima_Valor'),
                'unid_min': row.get('Pena_Minima_Unidade'),
                'unid_max': row.get('Pena_Maxima_Unidade')
            })
        
        # 2. TRATAMENTO DE VALORES NUMÉRICOS E UNIDADES
        try:
            pena_min_valor_raw = row.get('Pena_Minima_Valor')
            pena_max_valor_raw = row.get('Pena_Maxima_Valor')
            
            # Verifica se AMBOS os valores são válidos
            if pd.isna(pena_min_valor_raw) or pd.isna(pena_max_valor_raw):
                pulados += 1
                continue
            
            # Converte para float
            pena_min_valor = float(pena_min_valor_raw)
            pena_max_valor = float(pena_max_valor_raw)
            
            # Se os valores são zero ou negativos, pula
            if pena_min_valor <= 0 or pena_max_valor <= 0:
                pulados += 1
                continue
            
            # Obtém as unidades
            pena_min_unidade_raw = row.get('Pena_Minima_Unidade', 'mês')
            pena_max_unidade_raw = row.get('Pena_Maxima_Unidade', 'mês')
            
            pena_min_unidade = str(pena_min_unidade_raw).lower().strip() if pd.notna(pena_min_unidade_raw) else 'mês'
            pena_max_unidade = str(pena_max_unidade_raw).lower().strip() if pd.notna(pena_max_unidade_raw) else 'mês'
            
            if pena_min_unidade == 'nan':
                pena_min_unidade = 'mês'
            if pena_max_unidade == 'nan':
                pena_max_unidade = 'mês'

        except (ValueError, TypeError):
            pulados += 1
            continue

        # 3. CONVERSÃO PARA ANOS
        def converter_para_anos(valor, unidade):
            unidade_limpa = unidade.replace('ê', 'e').strip()
            if 'mes' in unidade_limpa or 'mês' in unidade:
                return valor / 12
            elif 'dia' in unidade_limpa:
                return valor / 360
            else:
                return valor

        pena_min_anos = converter_para_anos(pena_min_valor, pena_min_unidade)
        pena_max_anos = converter_para_anos(pena_max_valor, pena_max_unidade)
        
        if pena_min_anos > pena_max_anos:
            pena_min_anos, pena_max_anos = pena_max_anos, pena_min_anos
            
        # 4. CRIAÇÃO DA CHAVE E DADOS
        if artigo_completo and descricao and pena_min_anos > 0 and pena_max_anos > 0:
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
                'unidade_original_max': pena_max_unidade,
                'tipo_pena': row.get('Tipo_Pena', 'Reclusão')
            }
            processados += 1
        else:
            pulados += 1
    
    return crimes_dict, processados, pulados, art206_debug

# --- Carregar dados DIRETAMENTE DA URL ---
df = pd.DataFrame()
crimes_data = {}
carregamento_sucesso = False
total_processados = 0
total_pulados = 0
debug_206 = []

try:
    codificacoes = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
    
    for encoding in codificacoes:
        try:
            df = pd.read_csv(CSV_URL, encoding=encoding, sep=',')
            st.success(f"✅ Dados carregados com sucesso! (Codificação: {encoding})")
            carregamento_sucesso = True
            break
        except Exception:
            continue
    
    if carregamento_sucesso:
        crimes_data, total_processados, total_pulados, debug_206 = processar_dados_crimes(df)
        if not crimes_data:
            st.error("❌ Os dados foram carregados, mas não foi possível processar nenhum crime.")
            carregamento_sucesso = False

except Exception as e:
    st.error(f"❌ Erro ao carregar arquivo da URL: {e}")
    carregamento_sucesso = False

# --- Sidebar (SÓ DEPOIS DE CARREGAR) ---
st.sidebar.header("💡 Sobre")
st.sidebar.write("**Base Legal:** Art. 68 do Código Penal")
st.sidebar.write(f"**📊 Total de linhas no CSV:** {len(df) if not df.empty else 0}")
st.sidebar.write(f"**✅ Crimes processados:** {total_processados}")
st.sidebar.write(f"**⏭️ Crimes pulados:** {total_pulados}")

# 🔥 DEBUG DO ART. 206
if debug_206:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 DEBUG: Art. 206 Encontrado!")
    for info in debug_206:
        st.sidebar.write(f"**Linha {info['linha']}:**")
        st.sidebar.write(f"- Artigo: {info['artigo_completo']}")
        st.sidebar.write(f"- Pena Min: {info['pena_min']} {info['unid_min']}")
        st.sidebar.write(f"- Pena Max: {info['pena_max']} {info['unid_max']}")
        st.sidebar.write("---")
else:
    st.sidebar.warning("⚠️ Art. 206 NÃO encontrado no CSV!")

if st.sidebar.button("🔄 Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()

# Busca na sidebar
st.sidebar.write("**🔍 Buscar crime:**")
busca = st.sidebar.text_input("Digite o artigo ou descrição:")

if busca and crimes_data:
    crimes_filtrados = {k: v for k, v in crimes_data.items() if busca.lower() in k.lower()}
    st.sidebar.write(f"**Resultados ({len(crimes_filtrados)}):**")
    for chave in list(crimes_filtrados.keys())[:5]:
        crime_info = crimes_filtrados[chave]
        st.sidebar.write(f"**{crime_info['artigo']}** - Pena: {crime_info['pena_min']:.1f}-{crime_info['pena_max']:.1f} anos")

# Se não há dados, para aqui
if not crimes_data or not carregamento_sucesso:
    st.warning("⚠️ Aguardando carregamento do dataset...")
    st.stop()

# ------------------------------------------------------------------
## 1️⃣ Fase 1: Pena Base
# ------------------------------------------------------------------

st.header("1️⃣ Fase 1: Pena Base e Circunstâncias (Art. 59 CP)")
col1, col2 = st.columns([2, 1])

with col1:
    crime_selecionado = st.selectbox("Selecione o Crime:", options=list(crimes_data.keys()))
    crime_info = crimes_data[crime_selecionado]
    min_pena = crime_info['pena_min']
    max_pena = crime_info['pena_max']
    
    st.write(f"**Artigo:** {crime_info['artigo']}")
    st.write(f"**Tipo penal:** {crime_info['tipo_penal']}")
    st.write(f"**Descrição:** {crime_info['descricao_completa']}")
    st.write(f"**Pena original:** {crime_info['pena_min_original']} {crime_info['unidade_original_min']} a {crime_info['pena_max_original']} {crime_info['unidade_original_max']}")

with col2:
    range_pena = max_pena - min_pena 
    circunstancia = st.slider("Circunstâncias Judiciais Desfavoráveis (Art. 59):", 0, 8, 0)
    aumento_por_circunstancia = (range_pena / 8) if range_pena > 0 else 0
    pena_base_inicial = min_pena
    ajuste_circunstancia = circunstancia * aumento_por_circunstancia
    pena_base_ajustada = min(max_pena, pena_base_inicial + ajuste_circunstancia)
    
    st.write(f"**Pena prevista:** {min_pena:.1f} a {max_pena:.1f} anos")
    st.write(f"**Pena base inicial:** {pena_base_inicial:.1f} anos")
    st.write(f"**Ajuste:** +{ajuste_circunstancia:.1f} anos")
    st.success(f"**PENA BASE FINAL: {pena_base_ajustada:.1f} anos**")

## 2️⃣ Fase 2
st.header("2️⃣ Fase 2: Atenuantes e Agravantes (Art. 61, 62 e 65 CP)")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔽 Atenuantes")
    atenuantes = st.multiselect("Selecione:", [
        "Menor de 21 anos", "Maior de 70 anos", "Desconhecimento da lei",
        "Motivo de relevante valor social/moral", "Arrependimento espontâneo",
        "Reparação do dano", "Coação resistível", "Ordem superior",
        "Violenta emoção", "Confissão espontânea", "Influência de multidão"
    ])

with col2:
    st.subheader("🔼 Agravantes")
    agravantes = st.multiselect("Selecione:", [
        "Reincidência", "Motivo fútil ou torpe", "Traição/emboscada",
        "Veneno/fogo/explosivo", "Meio cruel", "Perigo comum",
        "Crime contra família", "Abuso de autoridade", "Violência doméstica",
        "Crime contra criança/idoso", "Embriaguez preordenada"
    ])

## 3️⃣ Fase 3
st.header("3️⃣ Fase 3: Majorantes e Minorantes")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Majorantes")
    majorantes = st.multiselect("Causas de aumento:", [
        "Uso de arma", "Violência grave", "Concurso de pessoas",
        "Restrição à liberdade", "Abuso de confiança", "Continuidade delitiva"
    ])

with col2:
    st.subheader("📉 Minorantes")
    minorantes = st.multiselect("Causas de diminuição:", [
        "Valor ínfimo", "Arrependimento posterior", "Privilégio",
        "Tentativa", "Participação de menor importância"
    ])

## 4️⃣ Cálculo
st.header("4️⃣ Cálculo Final")

if st.button("🎯 Calcular Pena Definitiva", type="primary"):
    
    pena_provisoria = pena_base_ajustada
    calculo = f"| Etapa | Valor | Ajuste |\n|---|---|---|\n| Pena Base | {pena_base_ajustada:.1f} anos | - |\n"
    
    # Atenuantes
    ajuste_2fase = pena_base_ajustada * (1/6)
    ajustes_aten = []
    for i, _ in enumerate(atenuantes, 1):
        if (pena_provisoria - ajuste_2fase) >= min_pena:
            pena_provisoria -= ajuste_2fase
            ajustes_aten.append(ajuste_2fase)
            calculo += f"| Atenuante {i} | {pena_provisoria:.1f} anos | -{ajuste_2fase:.1f} |\n"
        else:
            red = pena_provisoria - min_pena
            if red > 0.05:
                pena_provisoria = min_pena
                ajustes_aten.append(red)
                calculo += f"| Atenuante {i} | {min_pena:.1f} anos | -{red:.1f} (Súmula 231) |\n"
    
    # Agravantes
    ajustes_agra = []
    for i, _ in enumerate(agravantes, 1):
        pena_provisoria += ajuste_2fase
        ajustes_agra.append(ajuste_2fase)
        calculo += f"| Agravante {i} | {pena_provisoria:.1f} anos | +{ajuste_2fase:.1f} |\n"
    
    # Majorantes
    ajuste_3fase = pena_base_ajustada * (1/4)
    pena_definitiva = pena_provisoria
    ajustes_maj = []
    for i, _ in enumerate(majorantes, 1):
        pena_definitiva += ajuste_3fase
        ajustes_maj.append(ajuste_3fase)
        calculo += f"| Majorante {i} | {pena_definitiva:.1f} anos | +{ajuste_3fase:.1f} |\n"
    
    # Minorantes
    ajustes_min = []
    for i, _ in enumerate(minorantes, 1):
        if (pena_definitiva - ajuste_3fase) >= min_pena:
            pena_definitiva -= ajuste_3fase
            ajustes_min.append(ajuste_3fase)
            calculo += f"| Minorante {i} | {pena_definitiva:.1f} anos | -{ajuste_3fase:.1f} |\n"
        else:
            red = pena_definitiva - min_pena
            if red > 0.05:
                pena_definitiva = min_pena
                ajustes_min.append(red)
                calculo += f"| Minorante {i} | {min_pena:.1f} anos | -{red:.1f} (Súmula 231) |\n"
    
    pena_final = min(max_pena, max(min_pena, pena_definitiva))
    calculo += f"| **PENA FINAL** | **{pena_final:.1f} anos** | - |\n"
    
    st.markdown(calculo)
    
    # Regime
    st.header("5️⃣ Regime de Cumprimento")
    reincidente = "Reincidência" in agravantes
    
    if pena_final > 8:
        regime = "FECHADO"
        cor = "#ff4444"
    elif pena_final >= 4:
        regime = "SEMIABERTO" if not reincidente else "FECHADO"
        cor = "#ffaa00" if not reincidente else "#ff4444"
    else:
        regime = "ABERTO" if not reincidente else "SEMIABERTO"
        cor = "#44cc44" if not reincidente else "#ffaa00"
    
    st.markdown(f"""
    <div style="background:{cor}20; padding:20px; border-radius:10px; border-left:5px solid {cor};">
        <h2 style="color:{cor}">🔒 REGIME {regime}</h2>
        <p>Pena: {pena_final:.1f} anos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Substituição
    st.header("6️⃣ Substituição por PRD")
    pode_substituir = pena_final <= 4 and not reincidente
    cor_subst = "#44cc44" if pode_substituir else "#ff4444"
    texto = "CABE SUBSTITUIÇÃO" if pode_substituir else "NÃO CABE"
    
    st.markdown(f"""
    <div style="background:{cor_subst}20; padding:15px; border-radius:10px; border-left:5px solid {cor_subst};">
        <h3 style="color:{cor_subst}">{texto}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Gráfico
    st.header("📊 Visualização")
    fig = go.Figure(go.Waterfall(
        x=["Mín Legal", "Circunst.", "Atenuantes", "Agravantes", "Minorantes", "Majorantes", "Final"],
        y=[min_pena, ajuste_circunstancia, -sum(ajustes_aten), sum(ajustes_agra), -sum(ajustes_min), sum(ajustes_maj), pena_final],
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
        connector={"line":{"color":"rgb(63,63,63)"}},
        increasing={"marker":{"color":"#FF9800"}},
        decreasing={"marker":{"color":"#4CAF50"}},
        totals={"marker":{"color":"#2196F3"}}
    ))
    fig.update_layout(title="Composição da Pena", height=500)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.write("**⚖️ Ferramenta educacional - Art. 68 do CP**")
