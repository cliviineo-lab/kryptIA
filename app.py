import os
import sqlite3
import hashlib
import streamlit as st
from openai import OpenAI

# ---------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE & STYLE APPLE DARK
# ---------------------------------------------------------
st.set_page_config(
    page_title="KryptIA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Design Global Apple Dark */
    .stApp {
        background-color: #121214 !important;
        color: #f2f2f7 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif !important;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 5rem;
        max-width: 800px;
    }
    .apple-header {
        text-align: center;
        padding: 5px 0 15px 0;
    }
    .apple-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }
    .apple-subtitle {
        font-size: 0.85rem;
        color: #8e8e93;
    }
    
    /* Inputs & Formulaires */
    .stTextInput input {
        background-color: #1c1c1e !important;
        color: #ffffff !important;
        border: 1px solid #2c2c2e !important;
        border-radius: 12px !important;
    }
    .stButton button {
        background-color: #0a84ff !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    
    /* Bulles de chat */
    .stChatMessage {
        background-color: #1c1c1e !important;
        border: 1px solid #2c2c2e !important;
        border-radius: 16px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
    }
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid #3a3a3c !important;
        background-color: #1c1c1e !important;
    }
    .stChatInputContainer textarea { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INITIALISATION BASE DE DONNÉES SQLITE
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
        return True, "Compte créé avec succès !"
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

# Lancement BDD
init_db()

# ---------------------------------------------------------
# 3. CLIENT GROQ API
# ---------------------------------------------------------
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key) if api_key else None

# En-tête
st.markdown("""
<div class="apple-header">
    <div class="apple-title">KryptIA</div>
    <div class="apple-subtitle">Système Sécurisé Kryptia Core</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. COMPTE / AUTHENTIFICATION
# ---------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
    
    with tab1:
        username = st.text_input("Pseudo", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter", use_container_width=True):
            user = login_user(username, password)
            if user:
                st.session_state.user = username
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Pseudo ou mot de passe incorrect.")

    with tab2:
        new_user = st.text_input("Choisis un Pseudo", key="reg_user")
        new_pass = st.text_input("Choisis un Mot de passe", type="password", key="reg_pass")
        if st.button("S'inscrire", use_container_width=True):
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
# 5. ECRAN DE CHAT (UTILISATEUR CONNECTÉ)
# ---------------------------------------------------------
with st.sidebar:
    st.write(f"👤 Connecté en tant que : **{st.session_state.user}**")
    if st.button("Déconnexion", use_container_width=True):
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

# Initialisation de l'historique de chat de la session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Bonjour {st.session_state.user}. Je suis KryptIA. Comment puis-je t'aider aujourd'hui ?"}
    ]

# Affichage des messages avec les avatars 👻 et 👽
for msg in st.session_state.messages:
    avatar = "👻" if msg["role"] == "user" else "👽"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# Entrée du texte
if prompt := st.chat_input("Posez votre question..."):
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
