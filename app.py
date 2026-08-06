import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# ------------------------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE & STYLES PUREMENT SCI-FI
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="HUD Assistant Kimi",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Élimination des barres et marges natives Streamlit */
    header, footer, #MainMenu { visibility: hidden !important; }
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }
    .stApp { background-color: #02070d; }

    /* Sidebar futuriste */
    section[data-testid="stSidebar"] {
        background-color: #041424 !important;
        border-right: 1px solid #00f0ff !important;
    }

    /* Bulles de Chat Style FUI */
    .bot-reply {
        background: rgba(0, 240, 255, 0.08);
        border-left: 3px solid #00f0ff;
        padding: 12px;
        border-radius: 4px;
        color: #8be4f0;
        font-family: monospace;
        margin-bottom: 12px;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.1);
    }

    .user-msg {
        background: rgba(255, 0, 127, 0.08);
        border-right: 3px solid #ff007f;
        padding: 12px;
        border-radius: 4px;
        color: #ff8ce0;
        font-family: monospace;
        text-align: right;
        margin-bottom: 12px;
        box-shadow: 0 0 10px rgba(255, 0, 127, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. GESTION DE L'ÉTAT ET SIDEBAR
# ------------------------------------------------------------------------------
if "active_section" not in st.session_state:
    st.session_state.active_section = "CORE_CHAT"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Récupération du paramètre d'URL (envoyé par le HUD SVG)
nav_param = st.query_params.get("nav")
if nav_param and nav_param != st.session_state.active_section:
    st.session_state.active_section = nav_param

with st.sidebar:
    st.title("⚙️ OPTION SYSTEME")
    
    selected_model = st.selectbox(
        "Modèle Moonshot",
        options=["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        index=0
    )

    temperature = st.slider("Température (Créativité)", 0.0, 1.0, 0.7, 0.1)

    st.markdown("---")
    
    # Navigation manuelle de secours
    selected_nav = st.selectbox(
        "Secteur Sélectionné", 
        ["CORE_CHAT", "CAMERA", "MODES", "MEDIA", "LIBRARY", "EXIT", "PURGE", "NETWORK", "CONFIG"],
        index=["CORE_CHAT", "CAMERA", "MODES", "MEDIA", "LIBRARY", "EXIT", "PURGE", "NETWORK", "CONFIG"].index(st.session_state.active_section)
    )
    if selected_nav != st.session_state.active_section:
        st.session_state.active_section = selected_nav
        st.query_params["nav"] = selected_nav
        st.rerun()

    if st.button("🗑️ Vider la mémoire", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Client Moonshot AI
moonshot_key = st.secrets.get("MOONSHOT_API_KEY")
client = OpenAI(api_key=moonshot_key, base_url="https://api.moonshot.cn/v1") if moonshot_key else None

# ------------------------------------------------------------------------------
# 3. COMPOSANT HUD SVG (8 SECTEURS + AUDIO SYNTHÉTIQUE + FULLSCREEN)
# ------------------------------------------------------------------------------
def render_hud():
    active = st.session_state.active_section
    
    hud_html = f"""
    <style>
      .sector-group {{ transition: all 0.2s ease; cursor: pointer; }}
      .sector-group:hover path {{ fill: rgba(0, 240, 255, 0.25); stroke: #00f0ff; }}
      .active path {{ fill: rgba(43, 240, 118, 0.2) !important; stroke: #2bf076 !important; }}
      .active text {{ fill: #2bf076 !important; font-weight: bold; }}
    </style>

    <div style="text-align: center; margin-bottom: 5px;">
        <button onclick="toggleFullScreen(); playBeep(800, 0.05);" style="
            background: rgba(0, 240, 255, 0.1); 
            border: 1px solid #00f0ff; 
            color: #00f0ff; 
            padding: 6px 16px; 
            border-radius: 4px; 
            font-family: monospace; 
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);">
            ⛶ MODE PLEIN ÉCRAN
        </button>
    </div>

    <div style="display:flex; justify-content:center; align-items:center; height: 420px;">
      <svg viewBox="0 0 1000 1000" style="width:100%; max-width:440px; height:auto; filter:drop-shadow(0 0 6px rgba(0,240,255,0.4));">
        <circle cx="500" cy="500" r="460" stroke="#00d5ff" stroke-width="1.2" stroke-dasharray="3 6" fill="none" opacity="0.35" />
        <circle cx="500" cy="500" r="320" stroke="#00d5ff" stroke-width="1.2" fill="none" opacity="0.35" />
        <circle cx="500" cy="500" r="180" stroke="#00d5ff" stroke-width="1.2" fill="none" opacity="0.35" />
        
        <!-- NOYAU CENTRAL CORE -->
        <g onclick="selectMenu('CORE_CHAT')" style="cursor:pointer;" class="{'active' if active == 'CORE_CHAT' else ''}">
            <circle cx="500" cy="500" r="80" fill="#04192d" stroke="#00f0ff" stroke-width="3" />
            <text x="500" y="505" fill="#00f0ff" font-size="13" font-weight="bold" text-anchor="middle" font-family="monospace">KIMI CORE</text>
        </g>
        
        <!-- 8 SECTEURS CIRCULAIRES -->
        <g id="menu-items">
          <g class="sector-group {'active' if active == 'CAMERA' else ''}" onclick="selectMenu('CAMERA')">
            <path d="M 445 315 A 190 190 0 0 1 555 315 L 585 225 A 280 280 0 0 0 415 225 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5"/>
            <text x="500" y="270" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">CAMERA</text>
          </g>
          <g class="sector-group {'active' if active == 'MODES' else ''}" onclick="selectMenu('MODES')">
            <path d="M 575 345 A 190 190 0 0 1 655 425 L 725 385 A 280 280 0 0 0 615 275 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5"/>
            <text x="645" y="355" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">MODES</text>
          </g>
          <g class="sector-group {'active' if active == 'MEDIA' else ''}" onclick="selectMenu('MEDIA')">
            <path d="M 685 445 A 190 190 0 0 1 685 555 L 775 585 A 280 280 0 0 0 775 415 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5"/>
            <text x="730" y="500" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">MEDIA</text>
          </g>
          <g class="sector-group {'active' if active == 'LIBRARY' else ''}" onclick="selectMenu('LIBRARY')">
            <path d="M 655 575 A 190 190 0 0 1 575 655 L 615 725 A 280 280 0 0 0 725 615 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5"/>
            <text x="645" y="645" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">LIBRARY</text>
          </g>
          <g class="sector-group {'active' if active == 'EXIT' else ''}" onclick="selectMenu('EXIT')">
            <path d="M 555 685 A 190 190 0 0 1 445 685 L 415 775 A 280 280 0 0 0 585 775 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5"/>
            <text x="500" y="730" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">EXIT</text>
          </g>
          <g class="sector-group {'active' if active == 'PURGE' else ''}" onclick="selectMenu('PURGE')">
            <path d="M 425 655 A 190 190 0 0 1 345 575 L 275 615 A 280 280 0 0 0 385 725 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5"/>
            <text x="355" y="645" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">PURGE</text>
          </g>
          <g class="sector-group {'active' if active == 'NETWORK' else ''}" onclick="selectMenu('NETWORK')">
            <path d="M 315 555 A 190 190 0 0 1 315 445 L 225 415 A 280 280 0 0 0 225 585 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5"/>
            <text x="270" y="500" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">NETWORK</text>
          </g>
          <g class="sector-group {'active' if active == 'CONFIG' else ''}" onclick="selectMenu('CONFIG')">
            <path d="M 345 425 A 190 190 0 0 1 425 345 L 385 275 A 280 280 0 0 0 275 385 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5"/>
            <text x="355" y="355" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">CONFIG</text>
          </g>
        </g>
      </svg>
    </div>

    <script>
      // API Web Audio : Génération d'effets sonores synthétiques
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      
      function playBeep(freq = 600, duration = 0.08) {{
        if (audioCtx.state === 'suspended') {{ audioCtx.resume(); }}
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }}

      // Sélection fluide sans page blanche
      function selectMenu(name) {{
        playBeep(1000, 0.06);
        const url = new URL(window.parent.location);
        url.searchParams.set('nav', name);
        window.parent.history.pushState({{}}, '', url);
        // Force la mise à jour douce de Streamlit sans recharger toute la fenêtre
        window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: name }}, '*');
        setTimeout(() => {{ window.parent.location.reload(); }}, 100);
      }}

      function toggleFullScreen() {{
        var doc = window.parent.document;
        var docEl = doc.documentElement;
        var requestFullScreen = docEl.requestFullscreen || docEl.webkitRequestFullScreen;
        var cancelFullScreen = doc.exitFullscreen || doc.webkitExitFullscreen;

        if (!doc.fullscreenElement && !doc.webkitFullscreenElement) {{
          requestFullScreen.call(docEl);
        }} else {{
          cancelFullScreen.call(doc);
        }}
      }}
    </script>
    """
    return components.html(hud_html, height=470)

render_hud()

# ------------------------------------------------------------------------------
# 4. CONSOLE DE CHAT INTERACTIVE
# ------------------------------------------------------------------------------
st.markdown(f"#### 🛰️ CONSOLE KIMI — MODULE : `<{st.session_state.active_section}>`", unsafe_allow_html=True)

# Affichage des messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg"><b>VOUS:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-reply"><b>KIMI ({st.session_state.active_section}):</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

# Entrée du Chat
if prompt := st.chat_input(f"Commande pour le module {st.session_state.active_section}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if not client:
        st.error("❌ Clé MOONSHOT_API_KEY non configurée.")
    else:
        with st.spinner("Transmission au noyau..."):
            try:
                api_messages = [{
                    "role": "system",
                    "content": f"Tu es l'IA du HUD futuriste. Tu réponds précisément dans le contexte du module : {st.session_state.active_section}."
                }]
                for m in st.session_state.messages:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    model=selected_model,
                    messages=api_messages,
                    temperature=temperature
                )

                bot_answer = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": bot_answer})
                st.rerun()

            except Exception as e:
                st.error(f"Erreur API Moonshot : {e}")
