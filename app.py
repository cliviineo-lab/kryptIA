import streamlit as st
from groq import Groq
import os

# --- CONFIGURATION PAGE MOBILE ---
st.set_page_config(
    page_title="Sci-Fi Hologram HUD",
    page_icon="🛸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- INJECTION CSS : SUPERPOSITION & GLASSMORPHISM ---
st.markdown("""
<style>
    /* Fond global */
    .stApp {
        background-color: #05070a;
        color: #00ff66;
        font-family: 'Courier New', monospace;
    }
    
    #MainMenu, footer, header {visibility: hidden;}

    /* 1. LE CERCLE EN ARRIÈRE-PLAN (FIXED BACKDROP) */
    .hud-bg-container {
        position: fixed;
        top: 15%;
        left: 50%;
        transform: translate(-50%, 0);
        z-index: 0; /* Derrière le chat */
        pointer-events: none; /* Laisse passer les clics au-travers si besoin */
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .hud-bg-circle {
        width: 220px;
        height: 220px;
        border-radius: 50%;
        border: 2px dashed rgba(0, 255, 102, 0.4);
        box-shadow: 0 0 30px rgba(0, 255, 102, 0.2), inset 0 0 20px rgba(0, 255, 102, 0.1);
        background: radial-gradient(circle, rgba(0,255,102,0.1) 0%, rgba(5,7,10,0.8) 70%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        animation: rotateBg 20s linear infinite;
    }

    @keyframes rotateBg {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    /* 2. LA FENÊTRE DE CHAT SUPERPOSÉE (GLASSMORPHISM) */
    .stMainBlockContainer {
        position: relative;
        z-index: 10; /* Au-dessus du cercle */
        padding-top: 1rem !important;
    }

    /* Conteneur de Chat semi-transparent */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(9, 14, 23, 0.75) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(0, 255, 102, 0.5) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8), 0 0 15px rgba(0, 255, 102, 0.2) !important;
    }

    /* Style du Bouton-Cercle de commande (s'il est affiché) */
    div.stButton > button {
        background: rgba(5, 7, 10, 0.6) !important;
        border: 1px solid #00ff66 !important;
        color: #00ff66 !important;
        font-family: 'Courier New', monospace !important;
        border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- GESTION DE L'ÉTAT ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = True

if "messages" not in st.session_state:
    st.session_state.messages = []

# GROQ CLIENT
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key) if api_key else None

# --- 1. RENDU DU CERCLE HUD (ARRIÈRE-PLAN PERMANENT) ---
st.markdown("""
<div class="hud-bg-container">
    <div class="hud-bg-circle">
        <span style="font-size: 11px; color: #00ff66; opacity: 0.8; font-weight: bold;">CORE SYSTEM</span>
        <span style="font-size: 9px; color: #00f3ff; opacity: 0.6;">[ HOLO-LINK ]</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 2. FENÊTRE DE CHAT EN AVANT-PLAN ---

# Barre de contrôle de la fenêtre
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("🛸 HUD CONSOLE // OVERLAY")
with col2:
    label_btn = "❌ MUTE" if st.session_state.chat_open else "💬 CHAT"
    if st.button(label_btn):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

# Fenêtre de Chat Flottante (Si activée)
if st.session_state.chat_open:
    with st.container(border=True):
        chat_box = st.container(height=320)
        
        with chat_box:
            if not st.session_state.messages:
                st.markdown("*[ FENÊTRE DE DIALOGUE ACTIVÉE - Cercle en arrière-plan ]*")
            for msg in st.session_state.messages:
                prefix = "🟢 > SYSTEM:" if msg["role"] == "assistant" else "👤 > USER:"
                st.markdown(f"**{prefix}** {msg['content']}")

        # Champ d'écriture
        if user_input := st.chat_input("Envoyer un ordre..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            if client:
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    )
                    bot_reply = response.choices[0].message.content
                except Exception as e:
                    bot_reply = f"[ERR] Transmission: {str(e)}"
            else:
                bot_reply = "[DEMO] Clé GROQ_API_KEY non configurée."

            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
