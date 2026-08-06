import streamlit as st
from openai import OpenAI

# 1. Configuration de la page
st.set_page_config(page_title="Kimi K3 Chat (Privé)", page_icon="🔒")

# 2. Vérification de la configuration des Secrets
if "MOONSHOT_API_KEY" not in st.secrets or "USERS" not in st.secrets:
    st.error("⚠️ Les secrets (MOONSHOT_API_KEY ou USERS) ne sont pas configurés.")
    st.stop()

# 3. Gestion de l'état d'authentification
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------------------------------------------------------
# ECRAN DE CONNEXION (S'affiche si l'utilisateur n'est pas connecté)
# -------------------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🔒 Connexion Bêta")
    st.write("Veuillez vous identifier pour accéder à l'application.")

    with st.form("login_form"):
        user_input = st.text_input("Nom d'utilisateur")
        password_input = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")

    if submit:
        # Récupération de la liste des utilisateurs autorisés dans les Secrets
        valid_users = st.secrets["USERS"]
        
        # Vérification des identifiants
        if user_input in valid_users and valid_users[user_input] == password_input:
            st.session_state.authenticated = True
            st.session_state.username = user_input
            st.success(f"Bienvenue {user_input} !")
            st.rerun()  # Recharge la page pour afficher l'application
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect.")
            
    # Arrête l'exécution du reste du code tant que l'utilisateur n'est pas connecté
    st.stop()

# -------------------------------------------------------------------
# APPLICATION PRINCIPALE (Accessible uniquement une fois connecté)
# -------------------------------------------------------------------

st.title(f"💬 Kimi K3 Assistant")

# Initialisation du client API
client = OpenAI(
    api_key=st.secrets["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.cn/v1",
)

# Gestion de l'historique de discussion
if "messages" not in st.session_state:
    st.session_state.messages = []

# Barre latérale (Sidebar) avec déconnexion et options
with st.sidebar:
    st.write(f"👤 Connecté en tant que : **{st.session_state.username}**")
    
    if st.button("🚪 Se déconnecter"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

# Affichage de l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Zone de saisie du message
if prompt := st.chat_input("Posez votre question à Kimi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="kimi-k3",
                messages=st.session_state.messages,
                stream=True,
            )
            response_text = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
