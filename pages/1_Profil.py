import streamlit as st
import gspread as gs
import pandas as pd

# title
st.title('Wo befindest du dich?')

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

# Define basic layout / columns
col1, col2 = st.columns(2)

# Create questionaire for user profile
with st.form("User_profil"):
    submitted = st.form_submit_button("Antworten speichern")
    with col1:
        st.subheader("Über dich")
        name_carer = st.text_input("Dein Name")
        alter_carer = st.number_input("Dein Alter")
        wohnsituation = st.selectbox("Name der betroffenen Person",
                                     ["Im selben haushalt", "Wohnitz in der Nähe", "Wohnitz nicht in der Nähe"])
        betreuung = st.slider("Wie ist die Betreuungsituation (100 = Ich betreue alleine)")
    with col2:
        st.subheader("Über die erkrankte Person")
        name_patient = st.text_input("Name der betroffenen Person")
        alter_patient = st.number_input("Alter der betroffenen Person")
        familiensituation = st.selectbox("Die zu betreuende Person ist mein/e",
                                         ["Mutter/Vater", "Schwester/Bruder", "PartnerIn", "Anderes"])


    # Store profile in DB
    if submitted:
        user_infos = [[name_carer, alter_carer, name_patient, alter_patient, wohnsituation, familiensituation, betreuung]]
        "C{0}:I{0}".format(st.session_state['User_index'])
        ws.update("C{0}:I{0}".format(st.session_state['User_index']), user_infos)


