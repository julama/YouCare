import streamlit as st
import gspread as gs
import pandas as pd
#from yaml.loader import SafeLoader
#import streamlit_authenticator as stauth

# title
st.title('Erstelle ein Konto')

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
#store service account info in session
st.session_state['User_index'] = service_account_info

# Load google sheet as pandas frame
gc = gs.service_account_from_dict(service_account_info)
sh = gc.open_by_url(st.secrets["public_gsheets_url"])
ws = sh.worksheet('DB_login')
df = pd.DataFrame(ws.get_all_records())

# Create questionaire for user profile
with st.form("Konto"):
    name = st.text_input("Dein Benutzername")
    email = st.text_input("Deine Email Adresse")
    passwort = st.text_input("Wähle ein Passwort")
    submitted = st.form_submit_button("Antworten speichern")

    # Store profile in DB
    if submitted:
        if name in df["user"].values:
            st.warning('Bitte wähle einen neuen Username, da dieser bereits vergeben ist.')
        else:
            user_infos = [[name, email]]
            ws.append_rows(values=user_infos)
            st.session_state['User'] = name
            st.session_state['User_index'] = len(ws.col_values(1))
            st.info('Willkommen {}. Erstelle jetzt dein persönliches Profil'.format(name))
