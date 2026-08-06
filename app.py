import os
import uuid
import streamlit as st
from openai import OpenAI

# ---------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="KryptIA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. INITIALISATION DU CLIENT GROQ (VIA OPENAI SDK)
# ---------------------------------------------------------
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

client = None
if api_key:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

# ---------------------------------------------------------
# 3. CSS CUSTOM : VRAI APPLE DARK MODE & DESIGN NATIVE
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Reset & Fond Anthracite Apple */
    .stApp {
        background-color: #121214 !important;
        color: #f2f2f7 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Masquer le header et footer par défaut */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
        max-width: 800px;
    }

    /* En-tête Style iOS KryptIA */
    .apple-header {
        text-align: center;
        padding: 5px 0 10px 0;
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

    /* Style des boutons de la Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1c1c1e !important;
        border-right: 1px solid #2c2c2e !important;
    }
    
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #2c2c2e !important;
        border: 1px solid #3a3a3c !important;
        color: #0a84ff !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
        text-align: left !important;
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

    /* Avatars (Alien / Fantôme) */
    .stChatMessage [data-testid="stChatMessageAvatar"] {
        background-color: transparent !important;
        border: none !important;
        font-size: 1.6rem !important;
    }

    /* Champ de saisie iOS Sombre (Fix Fond Blanc) */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid #3a3a3c !important;
        background-color: #1c1c1e !important;
    }

    .stChatInputContainer textarea {
        color: #ffffff !important;
        background-color: transparent !important;
    }

    .stChatInputContainer:focus-within {
        border-color: #0a84ff !important;
        box-shadow: 0 0 8px rgba(10, 132, 255, 0.2) !important;
    }

    .stChatInputContainer button {
        color: #0a84ff !important;
        background-color: transparent !important;
    }

    /* Scrollbar discrète */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: #3a3a3c; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. GESTION DES DISCUSSIONS (MULTI-CHAT)
# ---------------------------------------------------------
if "chats" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.chats = {
        first_id: {
            "title": "Discussion 1",
            "messages": [
                {"role": "assistant", "content": "Bonjour. Je suis KryptIA. Comment puis-je vous aider aujourd'hui ?"}
            ]
        }
    }
    st.session_state.current_chat_id = first_id

def create_new_chat():
    new_id = str(uuid.uuid4())
    count = len(st.session_state.chats) + 1
    st.session_state.chats[new_id] = {
        "title": f"Discussion {count}",
        "messages": [
            {"role": "assistant", "content": "Bonjour. Je suis KryptIA. Comment puis-je vous aider aujourd'hui ?"}
        ]
    }
    st.session_state.current_chat_id = new_id

# ---------------------------------------------------------
# 5. SIDEBAR (GESTION DES CONVERSATIONS)
# ---------------------------------------------------------
with st.sidebar:
    st.subheader("💬 Conversations")
    
    if st.button("➕ Nouvelle discussion", use_container_width=True):
        create_new_chat()
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    for chat_id, chat_data in list(st.session_state.chats.items()):
        is_active = (chat_id == st.session_state.current_chat_id)
        icon = "🔹" if is_active else "💬"
        if st.button(f"{icon} {chat_data['title']}", key=f"btn_{chat_id}", use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Supprimer ce chat", use_container_width=True):
        if len(st.session_state.chats) > 1:
            del st.session_state.chats[st.session_state.current_chat_id]
            st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
            st.rerun()

# ---------------------------------------------------------
# 6. EN-TÊTE DE L'APPLICATION
# ---------------------------------------------------------
st.markdown("""
<div class="apple-header">
    <div class="apple-title">KryptIA</div>
    <div class="apple-subtitle">Propulsé par Groq & Llama 3.3</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. CHAT ACTIF & AFFICHAGE
# ---------------------------------------------------------
current_chat = st.session_state.chats[st.session_state.current_chat_id]
messages = current_chat["messages"]

if not client:
    st.error("⚠️ GROQ_API_KEY non configurée dans Streamlit Secrets.")

# Affichage avec les avatars 👻 (User) et 👽 (KryptIA)
for msg in messages:
    avatar = "👻" if msg["role"] == "user" else "👽"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# ---------------------------------------------------------
# 8. ENTREE UTILISATEUR (CHAT INPUT FIXÉ EN BAS)
# ---------------------------------------------------------
if prompt := st.chat_input("Posez votre question..."):
    # Titre auto pour la discussion
    user_msgs_count = len([m for m in messages if m["role"] == "user"])
    if user_msgs_count == 0:
        short_title = prompt[:20] + "..." if len(prompt) > 20 else prompt
        current_chat["title"] = short_title

    # Ajout message user
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👻"):
        st.write(prompt)

    # Réponse assistant
    if client:
        with st.chat_message("assistant", avatar="👽"):
            with st.spinner("Réflexion..."):
                try:
                    # Préparation des messages avec le system prompt
                    api_messages = [
                        {"role": "system", "content": "Tu es KryptIA, un assistant virtuel utile, poli, précis et concis. Ton interface est moderne et sécurisée."}
                    ]
                    for m in messages:
                        api_messages.append({"role": m["role"], "content": m["content"]})

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    reply = response.choices[0].message.content
                    st.write(reply)
                    messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {str(e)}")
