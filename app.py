import streamlit as st
from openai import OpenAI

# 1. Configuration de la page
st.set_page_config(page_title="Que souhaite-tu ?", page_icon="💬")
st.title("💬 Assistant Privé ")

# 2. Récupération sécurisée de la clé API via les Secrets
if "MOONSHOT_API_KEY" not in st.secrets:
    st.error("⚠️ La clé API Moonshot n'est pas configurée dans les Secrets Streamlit.")
    st.stop()

MOONSHOT_API_KEY = st.secrets["MOONSHOT_API_KEY"]

# 3. Initialisation du client compatible OpenAI
client = OpenAI(
    api_key=MOONSHOT_API_KEY,
    base_url="https://api.moonshot.cn/v1",
)

# 4. Gestion de la mémoire de discussion
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Bouton pour effacer l'historique dans le menu latéral
with st.sidebar:
    st.header("Options")
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

# 6. Affichage de l'historique des messages à l'écran
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. Gestion de la saisie utilisateur et appel d'API
if prompt := st.chat_input("Posez votre question à Kimi..."):
    # Stocke et affiche le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Réponse du modèle
    with st.chat_message("assistant"):
        try:
            # Appel API en mode Streaming
            stream = client.chat.completions.create(
                model="kimi-k3",
                messages=st.session_state.messages,
                stream=True,
            )
            # Affichage mot à mot
            response_text = st.write_stream(stream)
            # Enregistrement dans l'historique
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
