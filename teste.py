import streamlit as st

st.title("Meu programa")
st.write("Alô mundo")

nome = st.text_input("Digite o seu nome:")
if nome:
  st.write(nome.upper())

import streamlit as st
import random # Vamos usar para a aleatoriedade


st.title("🎲 O Sorteador de Decisões")
st.header("Se está em dúvida, deixe o código decidir!")


opcoes = [
    "✅ Sim, com certeza!",
    "❌ Não, nem pensar!!!",
    "⭐ Melhor esperar mais um pouco. Amadureça essa ideia",
    "😴 Esqueça esse assunto... Não pense mais sobre isso."
]



if st.button("Clique para receber sua DECISÃO!"):
    
    # 1. Escolha Aleatória
    decisao_escolhida = random.choice(opcoes)
    
    # 2. Resultado
    # Usamos o 'st.success' para destacar a mensagem
    st.success(f"✨ A Decisão é: **{decisao_escolhida}**")
    
    # 3. Efeito visual
    # O "confetti" é uma função simples mas muito visual!
    st.balloons()
    st.balloons()


st.caption(f"Psst... O programa tem {len(opcoes)} opções e escolheu uma delas de forma totalmente aleatória!!!!! ;)")
