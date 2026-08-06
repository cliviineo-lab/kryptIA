import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# ------------------------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="HUD Assistant Privé",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------------------
# 2. CLIENT MOONSHOT AI (KIMI)
# ------------------------------------------------------------------------------
moonshot_key = st.secrets.get("MOONSHOT_API_KEY")

client = None
if moonshot_key:
    client = OpenAI(
        api_key=moonshot_key,
        base_url="https://api.moonshot.cn/v1"
    )
else:
    st.warning("⚠️ Clé MOONSHOT_API_KEY non détectée dans st.secrets.")

# ------------------------------------------------------------------------------
# 3. CSS GLOBAL (Thème Futuriste & Boîte de Dialogue)
# ------------------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #02070d; }
    header, footer { visibility: hidden; }
    
    /* Style du conteneur de dialogue */
    .chat-box {
        background: rgba(4, 25, 45, 0.75);
        border: 1px solid #00f0ff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
        margin-top: 15px;
    }

    /* Bulles de réponse IA */
    .bot-reply {
        background: rgba(0, 240, 255, 0.1);
        border-left: 3px solid #00f0ff;
        padding: 12px;
        border-radius: 4px;
        color: #8be4f0;
        font-family: monospace;
        margin-bottom: 10px;
    }

    /* Bulles utilisateur */
    .user-msg {
        background: rgba(255, 0, 127, 0.1);
        border-right: 3px solid #ff007f;
        padding: 12px;
        border-radius: 4px;
        color: #ff8ce0;
        font-family: monospace;
        text-align: right;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. HUD INTERACTIF (SVG/JS)
# ------------------------------------------------------------------------------
try:
    with open("style.css", "r", encoding="utf-8") as f:
        css_content = f.read()
except FileNotFoundError:
    css_content = ""

def render_hud():
    hud_html = f"""
    <style>{css_content}</style>
    <div class="hud-container" style="display:flex; justify-content:center; align-items:center; position:relative;">
      <div class="glow-bg" style="position:absolute; width:450px; height:450px; background:radial-gradient(circle, rgba(0,213,255,0.12) 0%, rgba(2,7,13,0) 70%); border-radius:50%; pointer-events:none;"></div>

      <svg viewBox="0 0 1000 1000" class="hud-svg" style="width:100%; max-width:650px; height:auto; filter:drop-shadow(0 0 5px rgba(0,240,255,0.4));">
        <!-- Arrière-plan & Ticks -->
        <circle cx="500" cy="500" r="460" stroke="#00d5ff" stroke-width="1.2" stroke-dasharray="3 6" fill="none" opacity="0.35" />
        <circle cx="500" cy="500" r="320" stroke="#00d5ff" stroke-width="1.2" fill="none" opacity="0.35" />
        <circle cx="500" cy="500" r="180" stroke="#00d5ff" stroke-width="1.2" fill="none" opacity="0.35" />
        
        <!-- BOUTON CENTRAL ACCÈS CHAT (CORE) -->
        <g onclick="selectMenu('CHAT_CORE')" style="cursor:pointer;">
            <circle cx="500" cy="500" r="70" fill="#04192d" stroke="#00f0ff" stroke-width="3" />
            <text x="500" y="505" fill="#00f0ff" font-size="12" font-weight="bold" text-anchor="middle" font-family="monospace">OPEN CHAT</text>
        </g>
        
        <circle cx="500" cy="500" r="140" stroke="#00f0ff" stroke-width="10" stroke-dasharray="1 5" fill="none" opacity="0.25"/>

        <!-- 8 Rubriques Circulaires -->
        <g id="menu-items">
          <g class="sector-group" onclick="selectMenu('CAMERA')">
            <path d="M 445 315 A 190 190 0 0 1 555 315 L 585 225 A 280 280 0 0 0 415 225 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="500" y="270" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">CAMERA</text>
          </g>
          <g class="sector-group" onclick="selectMenu('MODES')">
            <path d="M 575 345 A 190 190 0 0 1 655 425 L 725 385 A 280 280 0 0 0 615 275 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="645" y="355" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">MODES</text>
          </g>
          <g class="sector-group active" onclick="selectMenu('MEDIA')">
            <path d="M 685 445 A 190 190 0 0 1 685 555 L 775 585 A 280 280 0 0 0 775 415 Z" fill="rgba(43,240,118,0.12)" stroke="#2bf076" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="730" y="500" fill="#2bf076" font-size="15" font-weight="bold" text-anchor="middle" font-family="monospace">MEDIA</text>
          </g>
          <g class="sector-group" onclick="selectMenu('LIBRARY')">
            <path d="M 655 575 A 190 190 0 0 1 575 655 L 615 725 A 280 280 0 0 0 725 615 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="645" y="645" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">LIBRARY</text>
          </g>
          <g class="sector-group" onclick="selectMenu('EXIT')">
            <path d="M 555 685 A 190 190 0 0 1 445 685 L 415 775 A 280 280 0 0 0 585 775 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="500" y="730" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">EXIT</text>
          </g>
          <g class="sector-group" onclick="selectMenu('PURGE')">
            <path d="M 425 655 A 190 190 0 0 1 345 575 L 275 615 A 280 280 0 0 0 385 725 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="355" y="645" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">PURGE</text>
          </g>
          <g class="sector-group" onclick="selectMenu('NETWORK')">
            <path d="M 315 555 A 190 190 0 0 1 315 445 L 225 415 A 280 280 0 0 0 225 585 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="270" y="500" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">NETWORK</text>
          </g>
          <g class="sector-group" onclick="selectMenu('CONFIG')">
            <path d="M 345 425 A 190 190 0 0 1 425 345 L 385 275 A 280 280 0 0 0 275 385 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="355" y="355" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">CONFIG</text>
          </g>
        </g>
      </svg>
    </div>

    <script>
      function selectMenu(name) {{
        const url = new URL(window.parent.location);
        url.searchParams.set('nav', name);
        window.parent.history.pushState({{}}, '', url);
        window.parent.location.reload();
      }}
    </script>
    """
    return components.html(hud_html, height=500)

# Affichage de l'interface graphique
render_hud()

# ------------------------------------------------------------------------------
# 5. BOÎTE DE DIALOGUE INTERACTIVE
# ------------------------------------------------------------------------------
active_section = st.query_params.get("nav", "MEDIA")

# Initialiser l'historique dans la session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Section d'accès / Panneau de contrôle du dialogue
st.markdown(f"#### 🛰️ BOÎTE DE DIALOGUE HUD — MODULE : `<{active_section}>`", unsafe_allow_html=True)

# Affichage des échanges dans le conteneur personnalisé
with st.container():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg"><b>VOUS:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-reply"><b>AGENT ({active_section}):</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

# Champ de texte / Entrée du Chat
if prompt := st.chat_input(f"Interroger l'agent dans le module {active_section}..."):
    
    # 1. Enregistrer le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Génération de la réponse si le dernier message vient de l'utilisateur
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    if not client:
        st.error("⚠️ Impossible de contacter Moonshot AI : Vérifiez votre clé MOONSHOT_API_KEY.")
    else:
        with st.spinner("Transmission au terminal Moonshot/Kimi..."):
            try:
                # Création du contexte système
                api_messages = [
                    {
                        "role": "system",
                        "content": f"Tu es l'IA intégrée au HUD futuriste. Tu assistes l'utilisateur dans le module actuellement ouvert : {active_section}."
                    }
                ]
                # Ajout de l'historique
                for m in st.session_state.messages:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                # Requête vers Kimi (Moonshot)
                response = client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=api_messages,
                    temperature=0.7
                )

                bot_answer = response.choices[0].message.content

                # Enregistrement de la réponse et rafraîchissement
                st.session_state.messages.append({"role": "assistant", "content": bot_answer})
                st.rerun()

            except Exception as e:
                st.error(f"Erreur d'accès réseau : {e}")
