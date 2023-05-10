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

#############
### Themen
#############

from utils import *

# Load the CSV file
#st.cache_resource
def load_data(path):
    return pd.read_csv(path)

file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)

## Load data from Notion
#notion = Client(auth="your_notion_api_key")
#database_id = "your_database_id"
#data = load_data_notion(database_id)

# Display checkboxes with random items
st.header("Meine Themen")
def keeper(key):
    st.session_state['_'+key] = st.session_state[key]

if st.session_state['profile']:
    profile = st.session_state.profile
    filtered_data, combined_data = filter_data_profile(data, profile)

    # Get unique values from filtered "Thema" and "Hauptbereich" columns
    unique_thema_filtered = filtered_data["Thema"].unique()
    unique_hauptbereich_filtered = filtered_data["Hauptbereich"].unique()

    # Get unique values from "Thema" and "Hauptbereich" columns
    unique_thema = data["Thema"].unique()
    unique_hauptbereich = data["Hauptbereich"].unique()

    # initalize selected Hauptbereich
    if not st.session_state['selected_hauptbereich']:
        selected_hauptbereich = dict([(i,False) for i in unique_hauptbereich])
        st.session_state['selected_hauptbereich'] = selected_hauptbereich
    else:
        selected_hauptbereich = st.session_state['selected_hauptbereich']

    # initalize selected Thema
    if not st.session_state['selected_thema']:
        selected_thema = dict([(i, False) for i in unique_thema])
        st.session_state['selected_thema'] = selected_thema
    else:
        selected_thema = st.session_state['selected_thema']


    # Hauptbereich Checkbox
    columns = st.columns(2)

    for idx, item in enumerate(unique_hauptbereich_filtered):
        if isinstance(item, str):
            column_idx = idx % 2

            if '_'+item not in st.session_state:
                st.session_state['_'+item]=False
            # Copy data from copied key to the widget's actual key
            st.session_state.item = st.session_state['_'+item]

            selected_hauptbereich[item] = columns[column_idx].checkbox(item, key=item, value=st.session_state.item,
                                                                       on_change=keeper, args=[item])


    # # # Reset corresponding "Thema" if "Hauptbereich" is deselected
    # for hauptbereich, is_selected in selected_hauptbereich.items():
    #     if not is_selected:
    #         for thema, _ in selected_thema.items():
    #             if data.loc[data["Thema"] == thema, "Hauptbereich"].iloc[0] == hauptbereich:
    #                 #st.write("do reset" + hauptbereich)
    #                 selected_thema[thema] = False
    #                 st.session_state['_' + thema] = False
    #                 st.session_state[thema] = False

    ## Filter Thema based on selection
    hauptbereich_keys = [k for k, v in selected_hauptbereich.items() if v]
    mask_thema = data[data["Hauptbereich"].isin(hauptbereich_keys)]
    unique_thema_filtered = mask_thema["Thema"].dropna().unique()

    hauptbereich_string = " und ".join(hauptbereich_keys)
    if hauptbereich_keys:
        st.header(f"Beim Thema {hauptbereich_string} beschäftigen mich:")

    # Themen Checkbox
    columns = st.columns(2)


    #selected_thema = dict([(i,False) for i in unique_thema_filtered])
    for idx, item in enumerate(unique_thema_filtered):
        if isinstance(item, str):
            column_idx = idx % 2

            if '_'+item not in st.session_state:
                st.session_state['_'+item]=False
            # Copy data from copied key to the widget's actual key
            st.session_state.item = st.session_state['_'+item]
            selected_thema[item] = columns[column_idx].checkbox(item, key=item, value=st.session_state.item, on_change=keeper, args=[item])


st.header("Meine Themen: Interaktiv")
# Display the search field
search = st.text_input("Was beschäftig dich gerade? Was hat dich in letzter Zeit herausgefordert?", value="", key="search_field")
search_icon = '<i class="fas fa-search"></i>'
st.markdown(search_icon, unsafe_allow_html=True)