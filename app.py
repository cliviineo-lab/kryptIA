import os
import sqlite3
import hashlib
import streamlit as st
from openai import OpenAI

# ---------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="KryptIA",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. DESIGN APPLE DARK / CSS GLOBAL UNIFIÉ
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Arrière-plan global Anthracite iOS */
    .stApp {
        background-color: #0d1117 !important;
        color: #f0f6fc !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif !important;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 6rem;
        max-width: 480px !important;
    }

    /* En-tête Apple */
    .apple-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .apple-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .apple-subtitle {
        font-size: 0.85rem;
        color: #8b949e;
        margin-top: 2px;
    }

    /* Badge de Statut */
    .status-badge {
        display: inline-block;
        background-color: #161b22;
        border: 1px solid #30363d;
        color: #3fb950;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 15px;
        text-align: center;
        width: 100%;
    }

    /* Onglets Connexion / Inscription Style iOS Segmented Control */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px !important;
        background-color: #161b22 !important;
        padding: 4px !important;
        border-radius: 14px !important;
        border: 1px solid #30363d !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px !important;
        background-color: transparent !important;
        border-radius: 10px !important;
        color: #8b949e !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border: none !important;
        flex: 1 !important;
        justify-content: center !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #30363d !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
    }

    /* Champs de saisie Formulaire */
    .stTextInput label {
        color: #8b949e !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        margin-bottom: 4px !important;
    }

    .stTextInput input {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    .stTextInput input:focus {
        border-color: #1f6feb !important;
    }

    /* Bouton Blanc Style Apple (Texte Sombre Lisible) */
    div.stButton > button {
        width: 100% !important;
        background-color: #ffffff !important;
        color: #0d1117 !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 24px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
        box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15) !important;
    }

    div.stButton > button:active {
        background-color: #e6e6e6 !important;
        transform: scale(0.98);
    }

    /* Bulles de Chat & Cartes Contextuelles */
    .stChatMessage {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 16px !important;
        padding: 14px 16px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    
    .stChatMessage p, .stChatMessage div {
        color: #f0f6fc !important;
        font-size: 0.95rem !important;
    }

    /* Barre de saisie du chat fixée en bas */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid #30363d !important;
        background-color: #161b22 !important;
    }
    
    .stChatInputContainer textarea { 
        color: #ffffff !important; 
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. BASE DE DONNÉES SQLITE
# ---------------------------------------------------------
DB_FILE = "kryptia_users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Compte créé ! Connecte-toi maintenant."
    except sqlite3.IntegrityError:
        return False, "Ce pseudo existe déjà."
    except Exception as e:
        return False, f"Erreur : {str(e)}"

def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

init_db()

# ---------------------------------------------------------
# 4. CLIENT GROQ API
# ---------------------------------------------------------
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key) if api_key else None

# ---------------------------------------------------------
# 5. HEADER PRINCIPAL
# ---------------------------------------------------------
st.markdown("""
<div class="apple-header">
    <div class="apple-title">KryptIA</div>
    <div class="apple-subtitle">Système Sécurisé Kryptia Core</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. AUTHENTIFICATION (FORMULAIRE CONNEXION / INSCRIPTION)
# ---------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
    
    with tab1:
        username = st.text_input("Pseudo", placeholder="Ex: Momo_Dev", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter", key="btn_login"):
            if username and password:
                user = login_user(username, password)
                if user:
                    st.session_state.user = username
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Pseudo ou mot de passe incorrect.")
            else:
                st.warning("Remplis tous les champs.")

    with tab2:
        new_user = st.text_input("Choisis un Pseudo", key="reg_user")
        new_pass = st.text_input("Choisis un Mot de passe", type="password", key="reg_pass")
        if st.button("S'inscrire", key="btn_reg"):
            if new_user and new_pass:
                success, msg = register_user(new_user, new_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Remplis tous les champs.")

    st.stop()

# ---------------------------------------------------------
# 7. ESPACE UTILISATEUR & CHAT
# ---------------------------------------------------------
with st.sidebar:
    st.write(f"👤 Connecté : **{st.session_state.user}**")
    if st.button("Déconnexion", use_container_width=True):
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

# Badge de statut en haut de l'espace utilisateur
st.markdown('<div class="status-badge">🟢 Système Sécurisé Kryptia Core v2.4</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Bonjour {st.session_state.user} !\nJe suis **KryptIA**. Comment puis-je t'aider dans vos projets aujourd'hui ?"}
    ]

for msg in st.session_state.messages:
    avatar = "👻" if msg["role"] == "user" else "👽"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# Gestion des entrées (Chat ou Raccourcis)
prompt = st.chat_input("Posez votre question à Kryptia...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👻"):
        st.write(prompt)

    if client:
        with st.chat_message("assistant", avatar="👽"):
            with st.spinner("Réflexion..."):
                try:
                    api_messages = [{"role": "system", "content": "Tu es KryptIA, un assistant virtuel intelligent, sécurisé et concis."}]
                    for m in st.session_state.messages:
                        api_messages.append({"role": m["role"], "content": m["content"]})

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    reply = response.choices[0].message.content
                    st.write(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {str(e)}")
