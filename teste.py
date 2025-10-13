import streamlit as st

st.title("Meu programa")
st.write("Alô mundo")

nome = st.text_input("Digite o seu nome:")
if nome:
  st.write(nome.upper())

import streamlit as st
import pandas as pd 

st.set_page_config(page_title="Ficha Rápida de Filme", page_icon="🎬")

st.title("🎬 Ficha Rápida de Filme")
titulo_filme = st.text_input(
    "Digite o título do filme:", 
    "A Origem" 
)

if titulo_filme.strip().lower() == "a origem":
    dados_filme = {
        "título": "A Origem (Inception)",
        "ano": 2010,
        "diretor": "Christopher Nolan",
        "sinopse": "Um ladrão que rouba segredos corporativos através do uso de tecnologia de compartilhamento de sonhos.",
        "nota_media": 8.8,
        "url_poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwMjg1MTc0Mw@@._V1_.jpg"
    }
elif titulo_filme.strip().lower() == "o poderoso chefão":
     dados_filme = {
        "título": "O Poderoso Chefão (The Godfather)",
        "ano": 1972,
        "diretor": "Francis Ford Coppola",
        "sinopse": "O patriarca de uma dinastia do crime organizado transfere o controle de seu império clandestino para seu filho relutante.",
        "nota_media": 9.2,
        "url_poster": "https://m.media-amazon.com/images/M/MV5BM2MyNjY2OTUtYjQ3OS00NjkxLWJmNWMtYzcyZThjYzk2MzllXkEyXkFqcGdeQXVyMjUzOTY1NTc@._V1_.jpg"
    }
else:
    dados_filme = None
    st.warning(f"Filme '{titulo_filme}' não encontrado. Tente 'A Origem'.")

if dados_filme:
    st.header(dados_filme["título"])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(dados_filme["url_poster"], caption="Pôster")
        
    with col2:
        st.metric(label="Nota Média", value=dados_filme["nota_media"])
        st.info(f"Ano: {dados_filme['ano']}")
        st.info(f"Diretor: {dados_filme['diretor']}")

    st.subheader("Sinopse")
    st.markdown(dados_filme["sinopse"])

st.caption("Para rodar: `streamlit run filme_simples.py`")

