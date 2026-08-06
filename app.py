import streamlit as st
from openai import OpenAI
import os

# ---------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="NOVA Core HUD",
    page_icon="⚡",
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

# Initialisation de l'état de la session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Système NOVA en ligne. En attente d'instructions."}
    ]
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False

# ---------------------------------------------------------
# 3. CSS CUSTOM : DESIGN SCI-FI / HUD MOBILE-FIRST
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Reset & Dark Cyberpunk Theme */
    .stApp {
        background-color: #050811;
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(0, 240, 255, 0.05) 0%, transparent 70%),
            linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 30px 30px, 30px 30px;
        color: #e0f7fc;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Masquer les éléments Streamlit superflus */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    /* Core HUD Central Animation */
    .hud-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 5vh;
        margin-bottom: 3vh;
    }

    .hud-title {
        font-size: 1.8rem;
        letter-spacing: 4px;
        color: #00f0ff;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.7);
        text-transform: uppercase;
        margin-bottom: 10px;
        font-weight: bold;
    }

    .hud-status {
        font-size: 0.8rem;
        color: #39ff14;
        letter-spacing: 2px;
        margin-bottom: 25px;
        text-shadow: 0 0 5px rgba(57, 255, 20, 0.5);
    }

    /* Boutons Streamlit en style Sci-Fi / Cyber Glass */
    div.stButton > button {
        background: rgba(0, 240, 255, 0.05) !important;
        border: 1px solid #00f0ff !important;
        color: #00f0ff !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.2), inset 0 0 15px rgba(0, 240, 255, 0.1) !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        background: rgba(0, 240, 255, 0.2) !important;
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.6) !important;
        color: #ffffff !important;
    }

    /* Bulles de Chat Sci-Fi */
    .stChatMessage {
        background: rgba(5, 15, 30, 0.75) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 10px !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.1) !important;
        backdrop-filter: blur(8px);
        margin-bottom: 12px;
    }

    /* Style du chat input */
    .stChatInputContainer {
        border-color: #00f0ff !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. EN-TÊTE DU HUD
# ---------------------------------------------------------
st.markdown("""
<div class="hud-container">
    <div class="hud-title">⚡ NOVA CORE v2.0 ⚡</div>
    <div class="hud-status">● SYSTEM STATUS: ONLINE</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. CONTROLES CENTRAUX (ACTIVER / DÉSACTIVER TERMINAL)
# ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    button_label = "CLOSE TERMINAL" if st.session_state.chat_active else "OPEN INTERFACE"
    if st.button(button_label, use_container_width=True):
        st.session_state.chat_active = not st.session_state.chat_active
        st.rerun()

# ---------------------------------------------------------
# 6. MODULE CHAT OVERLAY
# ---------------------------------------------------------
if st.session_state.chat_active:
    st.markdown("---")
    
    # Message d'avertissement si la clé API n'est pas définie
    if not client:
        st.error("⚠️ GROQ_API_KEY non détectée dans les secrets Streamlit.")
    
    # Affichage des messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Champ de saisie utilisateur
    if prompt := st.chat_input("Saisissez votre commande..."):
        # Ajout du message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Génération de la réponse via Groq (SDK OpenAI)
        if client:
            with st.chat_message("assistant"):
                with st.spinner("TRAITEMENT EN COURS..."):
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": "Tu es NOVA, une IA de bord Sci-Fi haute performance. Tes réponses sont concises, techniques et efficaces."},
                                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                            ],
                            temperature=0.7,
                            max_tokens=1024
                        )
                        reply = response.choices[0].message.content
                        st.write(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"Erreur de communication : {str(e)}")
