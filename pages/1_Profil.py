import streamlit as st
import gspread as gs
import pandas as pd
from utils import init_profile

# title
st.title('Wo befindest du dich?')

#intialize session state:
if 'profile' not in st.session_state:
    init_profile()

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
        alter_carer = st.number_input("Dein Alter", min_value=1,
                                      max_value=130,
                                      step=1,
                                      format="%d")
        wohnsituation = st.selectbox("Wohnsituation",
                                     ["im gleichen Haushalt", "unmittelbare Nähe", "weiter weg"])
        betreuung = st.slider(f"Ich betreue zu ... Prozent", min_value=0, max_value=100,
                              value=50)

    with col2:
        st.subheader("Über die betroffene Person")
        name_patient = st.text_input("Name")
        alter_patient = st.number_input("Alter", min_value=1,
                                        max_value=130,
                                        step=1,
                                        format="%d")
        beziehung = st.selectbox("Die zu betreuende Person ist mein/e",
                                 ["Mutter/Vater", "Schwester/Bruder", "PartnerIn", "Anderes"])
        diagnose = st.selectbox("Es besteht eine Alzheimer Diagnose", ["Ja", "Nein"])
        if diagnose=="Ja":
            Demenzstadium = st.selectbox("Demenzstadium", ["leicht", "mittel", "schwer"])
        else:
            Demenzstadium=""

    # Store profile in DB
    if submitted:
        user_infos = [[name_carer, alter_carer, name_patient, alter_patient, wohnsituation, beziehung, betreuung,diagnose, Demenzstadium]]
        #"C{0}:I{0}".format(st.session_state['User_index'])
        #ws.update("C{0}:I{0}".format(st.session_state['User_index']), user_infos)
        st.session_state.profile = {
            "Wohnsituation (!)": wohnsituation,
            "Betreeung": betreuung,
            "Beziehung": beziehung,
            "Diagnose (!)": diagnose,
            "Demenzstadium (!)": Demenzstadium
        }
