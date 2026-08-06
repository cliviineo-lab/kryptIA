import os
import uuid
import streamlit as st
from groq import Groq

# 1. Configuration de la page (Dark Mode style iOS)
st.set_page_config(page_title="KryptIA", page_icon="🔒", layout="centered")

# Style CSS sombre et épuré
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0b0e;
        color: #ffffff;
    }
    div.stButton > button {
        width: 100%;
        background-color: #1c1c24;
        color: #ffffff;
        border: 1px solid #2c2c38;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #2c2c38;
        border-color: #3c3c4c;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔒 KryptIA")

# 2. Clé API Groq
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Clé API Groq manquante. Configurez GROQ_API_KEY dans les Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# 3. Initialisation du gestionnaire de conversations
if "chats" not in st.session_state:
    # Structure : { chat_id: { "title": str, "messages": list } }
    first_id = str(uuid.uuid4())
    st.session_state.chats = {
        first_id: {
            "title": "Discussion 1",
            "messages": [
                {"role": "system", "content": "Tu es KryptIA, une IA sécurisée, intelligente et concise."}
            ]
        }
    }
    st.session_state.current_chat_id = first_id

# Fonction pour créer un nouveau chat
def create_new_chat():
    new_id = str(uuid.uuid4())
    count = len(st.session_state.chats) + 1
    st.session_state.chats[new_id] = {
        "title": f"Discussion {count}",
        "messages": [
            {"role": "system", "content": "Tu es KryptIA, une IA sécurisée, intelligente et concise."}
        ]
    }
    st.session_state.current_chat_id = new_id

# 4. Barre latérale (Sidebar) - Gestion des discussions
with st.sidebar:
    st.header("💬 KryptIA Conversations")
    
    # Bouton Nouvelle Discussion
    if st.button("➕ Nouvelle conversation"):
        create_new_chat()
        st.rerun()
        
    st.markdown("---")
    st.subheader("Vos discussions")
    
    # Liste dynamique des conversations
    for chat_id, chat_data in list(st.session_state.chats.items()):
        # Bouton sélectionné ou non
        is_active = (chat_id == st.session_state.current_chat_id)
        label = f"👉 {chat_data['title']}" if is_active else f"💬 {chat_data['title']}"
        
        if st.button(label, key=f"btn_{chat_id}"):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")
    
    # Bouton pour supprimer la conversation courante
    if st.button("🗑️ Supprimer cette conversation"):
        if len(st.session_state.chats) > 1:
            del st.session_state.chats[st.session_state.current_chat_id]
            st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
            st.rerun()
        else:
            # Réinitialiser si c'est la seule restante
            first_id = list(st.session_state.chats.keys())[0]
            st.session_state.chats[first_id]["messages"] = [
                {"role": "system", "content": "Tu es KryptIA, une IA sécurisée, intelligente et concise."}
            ]
            st.session_state.chats[first_id]["title"] = "Discussion 1"
            st.rerun()

# 5. Récupération du chat actif
current_chat = st.session_state.chats[st.session_state.current_chat_id]
messages = current_chat["messages"]

# 6. Affichage de l'historique du chat actif
for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 7. Entrée utilisateur et réponse de l'IA
if prompt := st.chat_input("Pose une question à KryptIA..."):
    # Si c'est le premier message utilisateur de la discussion, renommer le titre automatiquement
    user_msgs_count = len([m for m in messages if m["role"] == "user"])
    if user_msgs_count == 0:
        # Prendre les 25 premiers caractères du message comme titre
        short_title = prompt[:25] + "..." if len(prompt) > 25 else prompt
        current_chat["title"] = short_title

    # Affichage immédiat du message utilisateur
    st.chat_message("user").markdown(prompt)
    messages.append({"role": "user", "content": prompt})

    # Génération de la réponse via Groq
    with st.chat_message("assistant"):
        with st.spinner("KryptIA réfléchit..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                bot_reply = response.choices[0].message.content
                st.markdown(bot_reply)
                
                # Sauvegarde de la réponse
                messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()
                
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")
