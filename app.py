import streamlit as st
from openai import OpenAI

# ------------------------------------------------------------------------------
# 1. CONFIGURATION & STYLES CSS SUR-MESURE (ZÉRO IFRAME, ZÉRO PAGE BLANCHE)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Kimi Terminal Mobile",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    /* Masquage des éléments Streamlit inutiles */
    header, footer, #MainMenu { visibility: hidden !important; }
    .block-container { padding: 0.8rem !important; }
    .stApp { background-color: #02070d; }

    /* Titre futuriste */
    .hud-header {
        text-align: center;
        color: #00f0ff;
        font-family: monospace;
        font-size: 1.2rem;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 10px;
        text-shadow: 0 0 10px rgba(0,240,255,0.5);
    }

    /* Redéfinition des boutons Streamlit en Boutons Néon Tactiles */
    div.stButton > button {
        background: rgba(4, 25, 45, 0.8) !important;
        border: 1px solid #00d5ff !important;
        color: #9ee6f5 !important;
        font-family: monospace !important;
        font-size: 0.85rem !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        padding: 10px 5px !important;
        width: 100% !important;
        box-shadow: 0 0 8px rgba(0, 213, 255, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    div.stButton > button:active, div.stButton > button:focus {
        background: rgba(0, 240, 255, 0.25) !important;
        border-color: #00f0ff !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
    }

    /* Bulles de Chat FUI */
    .bot-reply {
        background: rgba(0, 240, 255, 0.08);
        border-left: 3px solid #00f0ff;
        padding: 10px;
        border-radius: 4px;
        color: #8be4f0;
        font-family: monospace;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }

    .user-msg {
        background: rgba(255, 0, 127, 0.08);
        border-right: 3px solid #ff007f;
        padding: 10px;
        border-radius: 4px;
        color: #ff8ce0;
        font-family: monospace;
        font-size: 0.9rem;
        text-align: right;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. GESTION DE SESSION & APIS
# ------------------------------------------------------------------------------
if "active_module" not in st.session_state:
    st.session_state.active_module = "CORE_CHAT"

if "messages" not in st.session_state:
    st.session_state.messages = []

moonshot_key = st.secrets.get("MOONSHOT_API_KEY")
client = OpenAI(api_key=moonshot_key, base_url="https://api.moonshot.cn/v1") if moonshot_key else None

# ------------------------------------------------------------------------------
# 3. INTERFACE TACTILE MOBILE (PANNEAU DE COMMANDE EN GRILLE)
# ------------------------------------------------------------------------------
st.markdown("<div class='hud-header'>🛰️ TERMINAL KIMI HUD</div>", unsafe_allow_html=True)

# Grille de 3 colonnes pour les boutons (Super facile à cliqueter au pouce)
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📷 CAMERA"): st.session_state.active_module = "CAMERA"
    if st.button("🌐 NETWORK"): st.session_state.active_module = "NETWORK"
    if st.button("⚙️ CONFIG"): st.session_state.active_module = "CONFIG"

with col2:
    if st.button("⚡ KIMI CORE"): st.session_state.active_module = "CORE_CHAT"
    if st.button("🔄 MODES"): st.session_state.active_module = "MODES"
    if st.button("🚫 EXIT"): st.session_state.active_module = "EXIT"

with col3:
    if st.button("🎬 MEDIA"): st.session_state.active_module = "MEDIA"
    if st.button("📚 LIBRARY"): st.session_state.active_module = "LIBRARY"
    if st.button("🔥 PURGE"): st.session_state.active_module = "PURGE"

st.markdown("---")

# ------------------------------------------------------------------------------
# 4. CHAT ET RÉPONSES EN DIRECT
# ------------------------------------------------------------------------------
st.markdown(f"#### 🛰️ MODULE SELECTIONNÉ : `<{st.session_state.active_module}>`", unsafe_allow_html=True)

# Historique
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg"><b>VOUS:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-reply"><b>KIMI ({st.session_state.active_module}):</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

# Input Chat
if prompt := st.chat_input(f"Commande pour {st.session_state.active_module}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if not client:
        st.error("❌ Clé API Moonshot manquante.")
    else:
        with st.spinner("Kimi analyse..."):
            try:
                response = client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {"role": "system", "content": f"Tu es l'IA du HUD. Réponds sous l'angle du module {st.session_state.active_module}."},
                        *st.session_state.messages
                    ],
                    temperature=0.7
                )
                bot_answer = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": bot_answer})
                st.rerun()
            except Exception as e:
                st.error(f"Erreur API : {e}")
