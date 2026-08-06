import streamlit as st
from openai import OpenAI
import os

# ---------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="KryptIA Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. INITIALISATION DU CLIENT GROQ (VIA OPENAI SDK)
# ---------------------------------------------------------
api_key = os.environ.get("GROQ_API_KEY", "")

client = None
if api_key:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour. Je suis KryptIA. Comment puis-je vous aider ?"}
    ]
if "chat_active" not in st.session_state:
    st.session_state.chat_active = True

# ---------------------------------------------------------
# 3. CSS CUSTOM : STYLE APPLE DARK MODE & ALIEN AVATARS
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Reset & Fond Anthracite Apple */
    .stApp {
        background-color: #121214 !important;
        color: #f2f2f7 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Nettoyage des menus Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 800px;
    }

    /* En-tête Style iOS KryptIA */
    .apple-header {
        text-align: center;
        padding: 10px 0 5px 0;
    }

    .apple-title {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 2px;
    }

    .apple-subtitle {
        font-size: 0.85rem;
        color: #8e8e93;
        font-weight: 400;
    }

    /* Bouton principal Bleu Apple */
    div.stButton > button {
        background-color: #1c1c1e !important;
        border: 1px solid #2c2c2e !important;
        color: #0a84ff !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    div.stButton > button:active {
        transform: scale(0.98);
        background-color: #2c2c2e !important;
    }

    /* Messages & Bulles de Chat */
    .stChatMessage {
        background-color: #1c1c1e !important;
        border: 1px solid #2c2c2e !important;
        border-radius: 16px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
    }

    /* Texte dans le Chat */
    .stChatMessage p, .stChatMessage div {
        color: #e5e5ea !important;
        font-size: 0.98rem !important;
    }

    /* Personnalisation des Avatars (Alien / Fantôme) */
    .stChatMessage [data-testid="stChatMessageAvatar"] {
        background-color: transparent !important;
        border: none !important;
        font-size: 1.6rem !important; /* Taille de l'émoji */
    }

    /* Champ de saisie iOS (SANS ROUGE) */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid #3a3a3c !important;
        background-color: #1c1c1e !important;
    }

    .stChatInputContainer:focus-within {
        border-color: #0a84ff !important;
        box-shadow: 0 0 8px rgba(10, 132, 255, 0.2) !important;
    }

    .stChatInputContainer button {
        color: #0a84ff !important;
    }

    /* Scrollbar discrète */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: #3a3a3c; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. EN-TÊTE DE L'APPLICATION KRYPTIA
# ---------------------------------------------------------
st.markdown("""
<div class="apple-header">
    <div class="apple-title">KryptIA</div>
    <div class="apple-subtitle">Propulsé par Groq & Llama 3.3</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. CONTROLES (OPTIONNEL : MASQUER / AFFICHER)
# ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    toggle_text = "Masquer la conversation" if st.session_state.chat_active else "Ouvrir l'assistant"
    if st.button(toggle_text, use_container_width=True):
        st.session_state.chat_active = not st.session_state.chat_active
        st.rerun()

# ---------------------------------------------------------
# 6. INTERFACE DE DISCUSSION
# ---------------------------------------------------------
if st.session_state.chat_active:
    st.write("")
    
    if not client:
        st.error("⚠️ GROQ_API_KEY non configurée.")

    # Affichage de l'historique avec avatars Alien/Fantôme
    for msg in st.session_state.messages:
        # User = Fantôme, Assistant = Alien
        avatar = "👻" if msg["role"] == "user" else "👽"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    # Zone de texte
    if prompt := st.chat_input("Posez votre question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👻"):
            st.write(prompt)

        if client:
            with st.chat_message("assistant", avatar="👽"):
                with st.spinner("Réflexion..."):
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                # System Prompt mis à jour avec le nom KryptIA
                                {"role": "system", "content": "Tu es KryptIA, un assistant virtuel utile, poli, précis et concis. Ton interface est moderne et sécurisée. Tu réponds dans la langue de l'utilisateur."},
                                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                            ],
                            temperature=0.7,
                            max_tokens=1024
                        )
                        reply = response.choices[0].message.content
                        st.write(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"Erreur : {str(e)}")
