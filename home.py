import streamlit as st
import gspread as gs
import pandas as pd
from config import to_hide_pages, to_show_pages
from st_pages import show_pages, hide_pages, show_pages_from_config
import hashlib
from streamlit_extras.switch_page_button import switch_page
st.set_page_config(layout="wide")

show_pages_from_config()
#show_pages(to_show_pages)
hide_pages(to_hide_pages)

# Hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#todo: add disclaimer-> Es ist eine Testversion, es kann sein...
st.title('Willkommen bei You+Care, deinem persönlichen Pflege Ratgeber')
st.write("• Erstelle zuerst ein Konto und wechsle dann zum Profil 👤")
st.write("• Das Profil kannst du jederzeit anpassen und verändern")
st.write("• Nachdem du dein Profil gespeichert hast, werden dir Themen vorgeschlagen")
st.write("• Wähle für dich relevante Themen und Unterkategorien aus")
st.write("• Wechsle dann zum Ratgeber :teacher: um mehr über die Themen zu erfahren")


# Google sheet DB login
creds = st.secrets["gcp_service_account"]
service_account_info = {
                "type" : creds["type"],
                "project_id" : creds["project_id"],
                "private_key_id" : creds["private_key_id"],
                "private_key" : creds["private_key"],
                "client_email" : creds["client_email"],
                "client_id" : creds["client_id"],
                "auth_uri" : creds["auth_uri"],
                "token_uri" : creds["token_uri"],
                "auth_provider_x509_cert_url" : creds["auth_provider_x509_cert_url"],
                "client_x509_cert_url" : creds["client_x509_cert_url"],
                }

# Load google sheet as pandas frame
gc = gs.service_account_from_dict(service_account_info)
sh = gc.open_by_url(st.secrets["public_gsheets_url"])
ws = sh.worksheet('DB_login')
df = pd.DataFrame(ws.get_all_records())

st.write("---")
# title
st.header('Erstelle ein Konto')

# Create questionaire for user registration
with st.form("Konto"):
    name = st.text_input("Dein Benutzername")
    email = st.text_input("Deine Email Adresse")
    password = st.text_input("Wähle ein Passwort", type="password")
    submitted = st.form_submit_button("Registrieren")

    if submitted:
        # Find the index of the first empty row
        user_index = len(ws.col_values(1))+1
        if name in df["user"].values:
            st.warning('Bitte wähle einen neuen Username, da dieser bereits vergeben ist.')
        elif email in df["email"].values:
            st.warning('Ein Konto für diese Email-Adresse existiert bereits')
        else:
            if len(password)<5:
                st.warning('Bitte wähle ein Passwort mit mindestens 5 Zeichen')
            # Register the user with streamlit-authenticator
            hashed_pwd = hash_password(password)
            user_infos = [[name, email, hashed_pwd]]
            ws.append_rows(user_infos)
            st.session_state['user'] = name
            st.session_state['User_index'] = user_index
            st.info('Willkommen {}. Erstelle jetzt dein persönliches Profil'.format(name))
            switch_page("Profil")

st.write("---")
# User Login
st.header('Ich habe bereits ein Konto')
with st.form("Login"):
    st.title("Login")
    login_name_or_email = st.text_input("Benutzername oder Email")
    login_password = st.text_input("Passwort", type="password")
    login_submitted = st.form_submit_button("Login")

    if login_submitted:
        is_authenticated=False
        # Check if the user provided a username or an email
        if "@" in login_name_or_email:  # It's an email
            stored_hashed_pwd = df.loc[df["email"] == login_name_or_email, "hashed_pwd"].values
        else:  # It's a username
            stored_hashed_pwd = df.loc[df["user"] == login_name_or_email, "hashed_pwd"].values

        # Verify the password
        hased_pwd_login = hash_password(login_password)
        if stored_hashed_pwd==hased_pwd_login:
            if "@" in login_name_or_email:  # It's an email
                st.session_state['User_index'] = df[df["email"] == login_name_or_email].index[0]+2
                st.success("Erfolgreich eingeloggt!")
                switch_page("Profil")
            else:  # It's a username
                st.session_state['User_index'] = df[df["user"] == login_name_or_email].index[0]+2
                st.success("Erfolgreich eingeloggt!")
                switch_page("Profil")
        else:
            st.warning("Falsches Passwort oder Username!")
st.write("---")
if st.button("Logout"):
    st.session_state.clear()
    st.info("Du bist ausgeloggt!")
