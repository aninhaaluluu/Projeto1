import streamlit as st

st.title("Meu programa")
st.write("Alô mundo")

nome = st.text_input("Digite o seu nome:")
if nome:
  st.write(nome.upper())


import streamlit as st

# --- Configuração da Página ---
st.set_page_config(page_title="Seletor de Cores", page_icon="🎨")

st.title("🎨 Visualizador de Cores Simples")
st.markdown("Escolha uma cor e veja-a aplicada em um painel!")

# --- O Widget Simples ---
# st.color_picker é um widget visualmente muito legal
cor_selecionada = st.color_picker("1. Escolha sua cor principal", "#3366FF") # Cor padrão: Azul Streamlit

# --- Visualização do Painel (O Fator Uau) ---

st.subheader("2. Painel de Amostra")

# 1. Crie um contêiner de colunas para o layout
col1, col2, col3 = st.columns(3)

# Cor de destaque (100% da cor escolhida)
with col1:
    st.markdown("Cor Principal")
    st.markdown(
        f"""
        <div style="background-color: {cor_selecionada}; padding: 30px; border-radius: 5px; height: 80px;">
        </div>
        <p style='text-align: center; font-weight: bold;'>{cor_selecionada}</p>
        """,
        unsafe_allow_html=True
    )

# Cor um pouco mais escura (simplesmente preto) para contraste
with col2:
    st.markdown("Cor de Contraste")
    cor_contraste = "#333333"
    st.markdown(
        f"""
        <div style="background-color: {cor_contraste}; padding: 30px; border-radius: 5px; height: 80px;">
        </div>
        <p style='text-align: center; font-weight: bold;'>{cor_contraste}</p>
        """,
        unsafe_allow_html=True
    )
    
# Cor de fundo simples (branco ou cinza claro)
with col3:
    st.markdown("Cor de Fundo")
    cor_fundo = "#F0F2F6"
    st.markdown(
        f"""
        <div style="background-color: {cor_fundo}; padding: 30px; border-radius: 5px; height: 80px; border: 1px solid #ccc;">
        </div>
        <p style='text-align: center; font-weight: bold;'>{cor_fundo}</p>
        """,
        unsafe_allow_html=True
    )

# --- Toque Final (Impressão) ---

st.markdown("---")
st.info(f"O Streamlit atualiza o painel instantaneamente toda vez que a cor muda no seletor.")
