import streamlit as st

st.title("Meu programa")
st.write("Alô mundo")

nome = st.text_input("Digite o seu nome:")
if nome:
  st.write(nome.upper())

import streamlit as st
import random # Vamos usar para a aleatoriedade

# --- Título com Emoji para ser mais amigável ---
st.title("🎲 O Sorteador de Decisões")
st.header("Se está em dúvida, deixe o código decidir!")

# --- Defina as opções de forma simples ---
opcoes = [
    "✅ Sim, com certeza!",
    "❌ Não, nem pensar.",
    "🤔 Talvez, tente novamente.",
    "⭐ Melhor esperar mais um pouco.",
    "🚀 Vá em frente!",
    "😴 Durma sobre o assunto."
]

# --- O Botão Mágico ---
# O Streamlit só executa o código dentro do 'if' se o botão for clicado
if st.button("Clique para receber sua DECISÃO!"):
    
    # 1. Escolha Aleatória
    decisao_escolhida = random.choice(opcoes)
    
    # 2. Mostra o Resultado
    # Usamos o 'st.success' para destacar a mensagem
    st.success(f"✨ A Decisão é: **{decisao_escolhida}**")
    
    # 3. Adiciona um toque visual (surpresa!)
    # O "confetti" é uma função simples mas muito visual!
    st.balloons()
    st.balloons()

# --- Toque Final (Explicação Simples) ---
st.caption(f"Psst... O programa tem {len(opcoes)} opções e escolheu uma delas de forma totalmente aleatória. Simples e funcional!")
