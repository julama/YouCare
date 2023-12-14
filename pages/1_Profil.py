import gspread as gs
from utils import *
from st_pages import add_page_title, hide_pages, show_pages
from config import to_hide_pages, to_show_pages
from streamlit_extras.switch_page_button import switch_page
hide_pages(to_hide_pages)
show_pages(to_show_pages)
add_page_title()

# title
st.title('Erstelle dein Profil')

#intialize session state:
if 'profile' not in st.session_state:
    init_profile()

if not st.session_state['User_index']:
    st.warning("Bitte logge dich zuerst ein")
    if st.button('Login'):
        switch_page("Login")
    else:
        st.stop()
user_index=st.session_state['User_index']

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

desired_row = df.iloc[user_index-2]
stored_profile = desired_row.loc['name_carer':'demenzstadium']
if not st.session_state.get('profile'):
    # Use stored values from the database if they exist, otherwise use defaults
    default_name_carer = stored_profile['name_carer'] if stored_profile['name_carer'] else ""
    #default_alter_carer = stored_profile['alter_carer'] if stored_profile['alter_carer'] else 60
    default_berufstaetigkeit= stored_profile['berufstaetigkeit'] if stored_profile['berufstaetigkeit'] else "Ja"
    default_name_patient = stored_profile['name_patient'] if stored_profile['name_patient'] else ""
    #default_alter_patient = stored_profile['alter_patient'] if stored_profile['alter_patient'] else 60
    default_beziehung = stored_profile['beziehung'] if stored_profile['beziehung'] else "PartnerIn"
    default_wohnsituation = stored_profile['wohnsituation'] if stored_profile['wohnsituation'] else "im gleichen Haushalt"
    default_diagnose = stored_profile['diagnose'] if stored_profile['diagnose'] else "Nein"
    default_demenzstadium = stored_profile['demenzstadium'] if stored_profile['demenzstadium'] else ""
    default_hilfen = stored_profile['hilfen'] if stored_profile['hilfen'] else "privates Umfeld hilft"
else:
    default_name_carer = st.session_state.profile.get("name_carer")
    #default_alter_carer = st.session_state.profile.get("alter_carer")
    default_berufstaetigkeit = st.session_state.profile.get("Berufstätigkeit")
    default_name_patient = st.session_state.profile.get("name_patient")
    default_beziehung = st.session_state.profile.get("Beziehung")
    default_wohnsituation = st.session_state.profile.get("Wohnsituation")
    default_demenzstadium = st.session_state.profile.get("Demenzstadium")
    default_diagnose = st.session_state.profile.get("Diagnose")
    default_hilfen = st.session_state.profile.get("Hilfen")

# Define basic layout / columns
col1, col2 = st.columns(2)
# Create questionaire for user profile
with col1:
    st.subheader("Über dich")
    name_carer = st.text_input("Dein Name", value=default_name_carer)
    # alter_carer = st.number_input("Dein Alter", min_value=1, max_value=130, step=1, format="%d",
    #                               value=default_alter_carer)
    wohnsituationen = ["im gleichen Haushalt", "unmittelbare Nähe", "weiter weg"]
    ws_index = wohnsituationen.index(default_wohnsituation)
    wohnsituation = st.selectbox("Wohnsituation", wohnsituationen, index=ws_index)

    berufstaetigkeiten = ["Ja", "Nein"]
    berufstaetigkeit_index = berufstaetigkeiten.index(default_berufstaetigkeit)
    berufstaetigkeit = st.selectbox("Ich bin berufstätig", berufstaetigkeiten, index=berufstaetigkeit_index)

    hilfen = ["privates Umfeld hilft", "professionelle Hilfe", "Nein"]
    hilfen_index = hilfen.index(default_hilfen)
    hilfe = st.selectbox("Ich habe Unterstützung/Hilfe bei der Betreuung", hilfen, index=hilfen_index)

with col2:
    st.subheader("Über die betroffene Person")
    name_patient = st.text_input("Name", value=default_name_patient)
    # alter_patient = st.number_input("Alter", min_value=1, max_value=130, step=1, format="%d",
    #                                 value=default_alter_patient)
    default_beziehung
    beziehung_choices = ["Mutter/Vater", "PartnerIn", "Anderes"]
    beziehung_index = beziehung_choices.index(default_beziehung)
    beziehung = st.selectbox("Die zu betreuende Person ist mein/e", beziehung_choices, index=beziehung_index)

    diagnose_choices = ["Ja", "Nein"]
    diagnose_index = diagnose_choices.index(default_diagnose)
    diagnose = st.selectbox("Ist eine Alzheimererkrankung oder eine andere Demenzform diagnostiziert?", diagnose_choices, index=diagnose_index)

    demenzstadium_choices = ["leicht", "mittel", "schwer", "kann ich nicht einschätzen"]
    demenzstadium_index = demenzstadium_choices.index(
        default_demenzstadium) if default_demenzstadium in demenzstadium_choices else 0
    demenzstadium = st.selectbox("Demenzstadium", demenzstadium_choices, index=demenzstadium_index)


# Store profile in DB
user_infos = [[name_carer, name_patient, wohnsituation, beziehung, berufstaetigkeit, diagnose, hilfe, demenzstadium]]
ws.update(f"D{user_index}:L{user_index}", user_infos)
st.session_state.profile = {
    "name_carer": name_carer,
    "name_patient": name_patient,
    "Wohnsituation": wohnsituation,
    "Beziehung": beziehung,
    "Berufstätigkeit": berufstaetigkeit,
    "Diagnose": diagnose,
    "Hilfen": hilfe,
    "Demenzstadium": demenzstadium


}

############
## Themen
############

file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)

#################
#### Meine Themen
################
st.write("---")
st.title("Was beschäftigt dich?")
st.subheader("Diese Themen passen zu deinem Profil. Markiere was für dich von Bedeutung ist:")

if st.session_state.get('profile'):
    profile = st.session_state.profile

    filtered_data, combined_data = filter_data_profile(data, profile)

    unique_thema_filtered = filtered_data["Thema"].unique()
    unique_hauptbereich_filtered = filtered_data["Hauptbereich"].unique()
    unique_thema = data["Thema"].unique()
    unique_hauptbereich = data["Hauptbereich"].unique()



    desired_row = df.iloc[user_index - 2]
    stored_profile = desired_row.loc['name_carer':'demenzstadium']

    if not st.session_state.get('profile'):
        # Use stored values from the database if they exist, otherwise use defaults
        default_name_carer = stored_profile['name_carer'] if stored_profile['name_carer'] else ""



    #initalize selected Hauptbereich

    if not st.session_state['selected_hauptbereich']:
        stored_hauptbereich = desired_row.loc['Alltag aktiv gestalten':'Vorsorge und Finanzierung']
        stored_hauptbereich_dict = {key: (value == "TRUE") for key, value in stored_hauptbereich.to_dict().items()}
        st.session_state['selected_hauptbereich'] = stored_hauptbereich_dict if stored_hauptbereich.any() else dict([(i, False) for i in unique_hauptbereich])

    # initalize selected Thema
    if not st.session_state['selected_thema']:
        stored_thema = desired_row.loc['Angenehme Aktivitäten gestalten':'Vorsorgeauftrag']
        stored_thema_dict = {key: (value == "TRUE") for key, value in stored_thema.to_dict().items()}
        st.session_state['selected_thema'] = stored_thema_dict if stored_thema.any() else dict([(i, False) for i in unique_hauptbereich])


    columns = st.columns(2)
    for idx, item in enumerate(unique_hauptbereich_filtered):
        if isinstance(item, str):
            column_idx = idx % 2
            # Checkbox for Hauptbereich
            checkbox_value = columns[column_idx].checkbox(item, key='_' + item, value=st.session_state['selected_hauptbereich'][item], on_change=keeper, args=[item])

            # Get Themas corresponding to the current Hauptbereich
            mask_thema = data[data["Hauptbereich"] == item]
            unique_thema_for_hauptbereich = mask_thema["Thema"].dropna().unique()

            # Multiselect for Themas beneath each Hauptbereich
            if checkbox_value:
                previous_themas = set(st.session_state.get('selected_thema_for_' + item, []))
                selected_themas_for_item = columns[column_idx].multiselect(f"Wähle passende Unterthemen",
                                                                           options=list(unique_thema_for_hauptbereich),
                                                                           default=list(previous_themas))

                current_themas = set(selected_themas_for_item)

                # Update session_state for selected_thema
                if previous_themas != current_themas:
                    for thema in unique_thema_for_hauptbereich:
                        st.session_state['selected_thema'][thema] = thema in current_themas

                    st.session_state['selected_thema_for_' + item] = list(current_themas)
                    st.experimental_rerun()

            columns[column_idx].write("---")

    ## Reset corresponding "Thema" if "Hauptbereich" is deselected
    for hauptbereich, is_selected in st.session_state['selected_hauptbereich'].items():
        if not is_selected:
            # Identify the Themas associated with the deselected Hauptbereich
            mask_thema = data[data["Hauptbereich"] == hauptbereich]
            deselected_themas = mask_thema["Thema"].dropna().unique()

            # Reset deselected Themas in session state
            for thema in deselected_themas:
                st.session_state['selected_thema'][thema] = False

                # For the multi-select state
                multiselect_key = 'selected_thema_for_' + hauptbereich
                if multiselect_key in st.session_state:
                    if thema in st.session_state[multiselect_key]:
                        st.session_state[multiselect_key].remove(thema)



    ######################
    #### Weitere Themen
    ######################
    st.subheader("Hier findest du weitere Themen")

    # Getting unique Hauptbereiche and Themas for the remaining data
    unique_weitere_hauptbereich = list(set(unique_hauptbereich) - set(unique_hauptbereich_filtered))
    unique_weitere_thema = list(set(unique_thema) - set(unique_thema_filtered))

    # Initialize the columns for this section
    columns = st.columns(2)

    # Display the Hauptbereiche with checkboxes, similar to before
    for idx, item in enumerate(unique_weitere_hauptbereich):
        if isinstance(item, str):
            column_idx = idx % 2

            # Checkbox for Hauptbereich
            checkbox_value = columns[column_idx].checkbox(item, key='_' + item,
                                                          value=st.session_state['selected_hauptbereich'][item],
                                                          on_change=keeper, args=[item])

            # Get Themas corresponding to the current Hauptbereich
            mask_thema = data[data["Hauptbereich"] == item]
            unique_thema_for_hauptbereich = mask_thema["Thema"].dropna().unique()

            ## Multiselect for Themas beneath each Hauptbereich
            if checkbox_value:
                previous_themas = set(st.session_state.get('selected_thema_for_' + item, []))
                selected_themas_for_item = columns[column_idx].multiselect(f"Wähle passende Unterthemen",
                                                                           options=list(unique_thema_for_hauptbereich),
                                                                           default=list(previous_themas))

                current_themas = set(selected_themas_for_item)

                # Update session_state for selected_thema
                if previous_themas != current_themas:
                    for thema in unique_thema_for_hauptbereich:
                        st.session_state['selected_thema'][thema] = thema in current_themas

                    st.session_state['selected_thema_for_' + item] = list(current_themas)
                    st.experimental_rerun()

                columns[column_idx].write("---")

    st.write("---")

    user_selection = [list(st.session_state["selected_hauptbereich"].values())+list(st.session_state['selected_thema'].values())[9:]]
    ws.update(f"M{user_index}:AQ{user_index}", user_selection)

    if st.button("Profil speichern"):
        st.session_state.click_count += 1
        elapsed_time = time.time() - st.session_state.start_time
        st.session_state.total_time_spent += elapsed_time
        st.session_state.start_time = time.time()
        switch_page("Ratgeber")



# ################
# ####### Interaktiv
# ################
# st.header("Meine Themen: Interaktiv")
# # Display the search field
# search = st.text_input("Was beschäftig dich gerade? Was hat dich in letzter Zeit herausgefordert?", value="", key="search_field")
# search_icon = '<i class="fas fa-search"></i>'
# st.markdown(search_icon, unsafe_allow_html=True)

