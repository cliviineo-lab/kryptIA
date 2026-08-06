import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# ------------------------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE STREAMLIT
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Assistant Privé HUD",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------------------
# 2. CONFIGURATION DE L'API MOONSHOT AI (KIMI)
# ------------------------------------------------------------------------------
# Récupération de la clé depuis st.secrets (ou variable locale)
moonshot_key = st.secrets.get("MOONSHOT_API_KEY")

client = None
if moonshot_key:
    # On spécifie le base_url OBLIGATOIRE de Moonshot pour éviter l'erreur 401 OpenAI
    client = OpenAI(
        api_key=moonshot_key,
        base_url="https://api.moonshot.cn/v1"
    )
else:
    st.error("⚠️ Clé API Moonshot manquante ! Ajoutez `MOONSHOT_API_KEY` dans vos secrets Streamlit.")

# ------------------------------------------------------------------------------
# 3. CSS GLOBAL (Thème Sombre & Style de Chat)
# ------------------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #02070d; }
    header, footer { visibility: hidden; }
    
    /* Style du conteneur de réponse */
    .chat-response {
        background: rgba(0, 240, 255, 0.05);
        border: 1px solid #00f0ff;
        border-radius: 8px;
        padding: 20px;
        margin-top: 10px;
        box-shadow: 0 0 15px rgba(0,240,255,0.15);
        color: #8be4f0;
        font-family: monospace;
    }
    
    /* Correction du champ d'entrée */
    .stTextInput input {
        background-color: #04192d !important;
        color: #00f0ff !important;
        border: 1px solid #00d5ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. COMPOSANT VISUEL HUD INTERACTIF (SVG/CSS)
# ------------------------------------------------------------------------------
# Chargement du fichier CSS externe si présent, sinon fallback
try:
    with open("style.css", "r", encoding="utf-8") as f:
        css_content = f.read()
except FileNotFoundError:
    css_content = ""

def render_hud():
    hud_html = f"""
    <style>{css_content}</style>
    <div class="hud-container" style="display:flex; justify-content:center; align-items:center; position:relative;">
      <div class="glow-bg" style="position:absolute; width:400px; height:400px; background:radial-gradient(circle, rgba(0,213,255,0.1) 0%, rgba(2,7,13,0) 70%); border-radius:50%; pointer-events:none;"></div>

      <svg viewBox="0 0 1000 1000" class="hud-svg" style="width:100%; max-width:700px; height:auto; filter:drop-shadow(0 0 4px rgba(0,240,255,0.4));">
        <defs>
          <path id="text-arc-1" d="M 680,240 A 310,310 0 0,1 780,720" fill="none"/>
        </defs>

        <!-- Arrière-plan & Ticks -->
        <circle cx="500" cy="500" r="460" stroke="#00d5ff" stroke-width="1.2" stroke-dasharray="3 6" fill="none" opacity="0.35" />
        <circle cx="500" cy="500" r="320" stroke="#00d5ff" stroke-width="1.2" fill="none" opacity="0.35" />
        <circle cx="500" cy="500" r="180" stroke="#00d5ff" stroke-width="1.2" fill="none" opacity="0.35" />
        <circle cx="500" cy="500" r="70" fill="#02070d" stroke="#00f0ff" stroke-width="2.5" />
        <circle cx="500" cy="500" r="140" stroke="#00f0ff" stroke-width="10" stroke-dasharray="1 5" fill="none" opacity="0.3"/>

        <!-- 8 Rubriques Circulaires -->
        <g id="menu-items">
          <!-- CAMERA -->
          <g class="sector-group" onclick="selectMenu('CAMERA')">
            <path d="M 445 315 A 190 190 0 0 1 555 315 L 585 225 A 280 280 0 0 0 415 225 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="500" y="270" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">CAMERA</text>
          </g>
          <!-- MODES -->
          <g class="sector-group" onclick="selectMenu('MODES')">
            <path d="M 575 345 A 190 190 0 0 1 655 425 L 725 385 A 280 280 0 0 0 615 275 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="645" y="355" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">MODES</text>
          </g>
          <!-- MEDIA (Actif - Vert) -->
          <g class="sector-group active" onclick="selectMenu('MEDIA')">
            <path d="M 685 445 A 190 190 0 0 1 685 555 L 775 585 A 280 280 0 0 0 775 415 Z" fill="rgba(43,240,118,0.12)" stroke="#2bf076" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="730" y="500" fill="#2bf076" font-size="15" font-weight="bold" text-anchor="middle" font-family="monospace">MEDIA</text>
          </g>
          <!-- LIBRARY -->
          <g class="sector-group" onclick="selectMenu('LIBRARY')">
            <path d="M 655 575 A 190 190 0 0 1 575 655 L 615 725 A 280 280 0 0 0 725 615 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="645" y="645" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">LIBRARY</text>
          </g>
          <!-- EXIT -->
          <g class="sector-group" onclick="selectMenu('EXIT')">
            <path d="M 555 685 A 190 190 0 0 1 445 685 L 415 775 A 280 280 0 0 0 585 775 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="500" y="730" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">EXIT</text>
          </g>
          <!-- PURGE -->
          <g class="sector-group" onclick="selectMenu('PURGE')">
            <path d="M 425 655 A 190 190 0 0 1 345 575 L 275 615 A 280 280 0 0 0 385 725 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="355" y="645" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">PURGE</text>
          </g>
          <!-- NETWORK -->
          <g class="sector-group" onclick="selectMenu('NETWORK')">
            <path d="M 315 555 A 190 190 0 0 1 315 445 L 225 415 A 280 280 0 0 0 225 585 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="270" y="500" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">NETWORK</text>
          </g>
          <!-- CONFIG -->
          <g class="sector-group" onclick="selectMenu('CONFIG')">
            <path d="M 345 425 A 190 190 0 0 1 425 345 L 385 275 A 280 280 0 0 0 275 385 Z" fill="rgba(4,25,45,0.6)" stroke="#00d5ff" stroke-width="1.5" style="cursor:pointer;"/>
            <text x="355" y="355" fill="#9ee6f5" font-size="15" text-anchor="middle" font-family="monospace">CONFIG</text>
          </g>
        </g>

        <!-- Éléments décoratifs et sous-menus -->
        <rect x="795" y="485" width="105" height="30" rx="3" fill="none" stroke="#00d5ff" stroke-width="1.5"/>
        <text x="805" y="505" fill="#00d5ff" font-size="11" font-family="monospace">0637_718-U</text>

        <rect x="910" y="485" width="80" height="30" rx="3" fill="rgba(255,0,127,0.15)" stroke="#ff007f" stroke-width="1.5"/>
        <text x="918" y="505" fill="#ff007f" font-size="11" font-weight="bold" font-family="monospace">STATION</text>
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
    return components.html(hud_html, height=520)

# Affichage du HUD SVG
render_hud()

# ------------------------------------------------------------------------------
# 5. LOGIQUE DU CHAT / MOONSHOT AI (KIMI)
# ------------------------------------------------------------------------------
# Lecture de la section sélectionnée via l'URL (par défaut MEDIA)
active_section = st.query_params.get("nav", "MEDIA")

st.markdown(f"### 💬 Assistant Privé — Module : `<{active_section}>`", unsafe_allow_html=True)

# Zone de saisie utilisateur
user_prompt = st.text_input("Saisissez votre commande ou question :", placeholder="ex: Comment fonctionne le module...")

if user_prompt:
    if not client:
        st.error("Impossible de contacter l'IA : Vérifiez la clé API Moonshot dans vos Secrets.")
    else:
        with st.spinner("Analyse par le système Kimi/Moonshot en cours..."):
            try:
                # Modèle Moonshot (Kimi) standard : moonshot-v1-8k
                response = client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {"role": "system", "content": f"Tu es l'IA de bord d'un HUD futuriste. Tu réponds sous le contexte du module : {active_section}."},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                
                # Affichage de la réponse du modèle
                reply = response.choices[0].message.content
                st.markdown(f'<div class="chat-response"><b>[SYSTEM RESPONSE]:</b><br><br>{reply}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
