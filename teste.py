import streamlit as st

st.title("Meu programa")
st.write("Alô mundo")

nome = st.text_input("Digite o seu nome:")
if nome:
  st.write(nome.upper())

import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="Calculadora de Idade", page_icon="🎂")

st.title("🎂 Calculadora de Idade e Aniversário")
st.markdown("Descubra quantos anos você tem e quantos dias faltam para a próxima festa!")

# --- 1. Entrada da Data de Nascimento ---
data_nascimento = st.date_input(
    "1. Selecione sua data de nascimento:",
    date(date.today().year - 20, 1, 1),
    max_value=date.today() 
)

# --- Variáveis de Data ---
data_hoje = date.today()

# 2.1. Calcular a Idade
def calcular_idade(data_nasc, data_atual):
    idade = data_atual.year - data_nasc.year
    if (data_atual.month, data_atual.day) < (data_nasc.month, data_nasc.day):
        idade -= 1
    return idade

# 2.2. Calcular Dias para o Aniversário
def dias_para_aniversario(data_nasc, data_atual):
    # Cria a data do próximo aniversário no ano atual
    proximo_aniv = date(data_atual.year, data_nasc.month, data_nasc.day)
    
    # Se o aniversário já passou este ano, muda para o próximo ano
    if proximo_aniv < data_atual:
        proximo_aniv = date(data_atual.year + 1, data_nasc.month, data_nasc.day)
        
    diferenca = proximo_aniv - data_atual
    return diferenca.days

idade_atual = calcular_idade(data_nascimento, data_hoje)
dias_restantes = dias_para_aniversario(data_nascimento, data_hoje)

# --- 3. Visualização do Resultado ---

st.subheader("2. Seus Resultados")

# Exibe a idade em destaque
st.metric(
    label="Sua Idade Atual é:",
    value=f"{idade_atual} anos"
)

col1, col2 = st.columns(2)

# O objeto timedelta é usado aqui
data_proximo_obj = data_hoje + timedelta(days=dias_restantes)
data_proximo_formatada = data_proximo_obj.strftime("%d de %B")

with col1:
    st.info("Dia do seu próximo aniversário:")
    st.markdown(f"**{data_proximo_formatada}**")

with col2:
    st.info("Dias restantes para a festa:")
    st.markdown(f"**{dias_restantes} dias**")

if dias_restantes == 0:
    st.balloons()
    st.success("🎉 FELIZ ANIVERSÁRIO! É hoje!")

st.markdown("---")
st.caption("Esta aplicação usa a biblioteca `datetime` do Python para cálculos de data e o `st.date_input` para entrada de dados.")
