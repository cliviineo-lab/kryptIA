import streamlit as st
from openai import OpenAI
import os

# ---------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="KryptIA",
    page_icon="🍎",
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
        {"role": "assistant", "content": "Bonjour. Comment puis-je vous aider aujourd'hui ?"}
    ]
if "chat_active" not in st.session_state:
    st.session_state.chat_active = True  # Activé par défaut pour plus de simplicité

# ---------------------------------------------------------
# 3. CSS CUSTOM : STYLE APPLE DARK MODE (ANTI-ROUGE FOCUS)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Reset & Fond Anthracite Apple (Reposant) */
    .stApp {
        background-color: #121214 !important;
        color: #f2f2f7 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Nettoyage des menus Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 800px;
    }

    /* En-tête Style iOS */
    .apple-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }

    .apple-title {
        font-size: 1.6rem;
        font-weight: 600;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 4px;
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
        padding: 12px 20px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
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
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }

    /* Texte dans le Chat (Gris voyant & très lisible) */
    .stChatMessage p, .stChatMessage div {
        color: #e5e5ea !important;
        font-size: 0.98rem !important;
        line-height: 1.5 !important;
    }

    /* Champ de saisie iOS (SANS CONTOUR ROUGE) */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid #3a3a3c !important;
        background-color: #1c1c1e !important;
    }

    /* Suppression de l'effet rouge Streamlit au clic / focus */
    .stChatInputContainer:focus-within, 
    .stChatInputContainer:focus,
    textarea:focus {
        border-color: #0a84ff !important; /* Devient bleu Apple au lieu de rouge */
        box-shadow: 0 0 8px rgba(10, 132, 255, 0.3) !important;
        outline: none !important;
    }

    .stChatInputContainer textarea {
        color: #ffffff !important;
        font-size: 0.95rem !important;
    }

    /* Modifie le bouton d'envoi (flèche) */
    .stChatInputContainer button {
        color: #0a84ff !important;
    }

    /* Scrollbar discrète */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-thumb {
        background: #3a3a3c;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True) 

# ---------------------------------------------------------
# 4. EN-TÊTE DE L'APPLICATION
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

    # Affichage de l'historique
    for msg in st.session_state.messages:
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
                                {"role": "system", "content": "Tu es un assistant virtuel utile, poli, précis et concis. Tu réponds dans la langue de l'utilisateur."},
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
