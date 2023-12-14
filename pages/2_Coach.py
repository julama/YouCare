from utils import *
import gspread as gs
from streamlit_extras.switch_page_button import switch_page
from config import to_hide_pages, emoji_dict
from st_pages import add_page_title, hide_pages, show_pages,show_pages_from_config
#show_pages(to_show_pages)
show_pages_from_config()
hide_pages(to_hide_pages)
add_page_title()

file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)

#intialize session state:
if 'profile' not in st.session_state:
    init_profile()

if not st.session_state['profile']:
    st.warning("Bitte erstelle zuerst ein Profil")
    st.stop()
else:
    profile = st.session_state.profile

emoji_values = list(emoji_dict.values())
data['emojis'] = emoji_values

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

user_index=st.session_state['User_index']
desired_row = df.iloc[user_index-2]
stored_total_time, stored_click_count = desired_row.loc['total_time_spent':'click_count']

st.write(" ")
st.write(" ")

selected_thema = st.session_state['selected_thema']
selected_hauptbereich = st.session_state['selected_hauptbereich']
store_user_selection = selected_hauptbereich, selected_thema

# Score Sortierkriterien based on profile and selection
filtered_data, combined_data = filter_data_profile(data, profile)

sel_thema, scores_other_topics, scores = scoring_function(data, selected_thema, selected_hauptbereich, profile)
random_thema = random_feed(scores_other_topics)
sel_thema_values = get_selected_thema(selected_thema)
data_sorted, your_feed, data_sorted_wo_selectd_hk, selected_hk = sort_score(random_thema, data, sel_thema_values, selected_hauptbereich, 6)

## Deine Themen
## Passende Unterthemen vorzuschlagen: deprecated;
# st.header('Deine Themen')
# cols = st.columns(3)
# for i in range(len(your_feed)):
#     j = (i % 3)
#     if cols[j].button(f"{emoji_dict[your_feed[i]]} {your_feed[i]}", key=f'feed_{i}'):
#         st.session_state.click_count += 1
#         elapsed_time = time.time() - st.session_state.start_time
#         st.session_state.total_time_spent += elapsed_time
#         st.session_state.start_time = time.time()
#         modified_string = umlauts(your_feed[i])
#         if modified_string in to_hide_pages:
#             switch_page(modified_string)
#         else:
#             st.info("Leider haben wir noch keinen Coach für dieses Thema")

## Empfehlungen Section
st.write("---")
e1, section_title, e12 = st.columns([10,8,10])
st.header('Deine Themen')
# Anzahl Thmen in "Deine themen"
n_themen = 2

#selected categories always on top of "Themen im Überblick"
categories = data_sorted_wo_selectd_hk['Hauptbereich'].unique()
categories = selected_hk+list(categories)
my_feed = categories[0:n_themen]

for category in my_feed:
    cat_title, cat_info = st.columns([1,8])
    with cat_info:
        st.write(" ")
        st.subheader(category)
    with cat_title:
        st.write(" ")
    if cat_title.button('ℹ️', key=f'{category}_info'):
        st.session_state.click_count += 1
        elapsed_time = time.time() - st.session_state.start_time
        st.session_state.total_time_spent += elapsed_time
        st.session_state.start_time = time.time()
        modified_category = umlauts(category)
        if modified_category in to_hide_pages:
            switch_page(modified_category)
        else:
            st.info("Leider haben wir noch keinen Coach für dieses Thema")

    thema_in_category = data[data['Hauptbereich'] == category]['Thema'].tolist()
    icon_in_category = data[data['Hauptbereich'] == category]['emojis'].tolist()
    cols = st.columns(3)

    for i in range(len(thema_in_category)):
        j = (i % 3)
        if cols[j].button(f'{icon_in_category[i]} {thema_in_category[i]}',key=f'{thema_in_category[i]}_{i}'):
            st.session_state.click_count += 1
            elapsed_time = time.time() - st.session_state.start_time
            st.session_state.total_time_spent += elapsed_time
            st.session_state.start_time = time.time()
            modified_thema = umlauts(thema_in_category[i])
            if modified_thema in to_hide_pages:
                switch_page(modified_thema)
            else:
                st.info("Leider haben wir noch keinen Coach für dieses Thema")
        st.write(" ")

## Empfehlungen Section
st.write("---")
e1, section_title, e12 = st.columns([10,8,10])
st.header('Weitere Themen für Dich')

#selected categories always on top of "Themen im Überblick"
weitere_themen = categories[n_themen:]

st.write(" ")
for category in weitere_themen:
    cat_title, cat_info = st.columns([1,8])
    with cat_info:
        st.write(" ")
        st.subheader(category)
    with cat_title:
        st.write(" ")
    if cat_title.button('ℹ️', key=f'{category}_info'):
        st.session_state.click_count += 1
        elapsed_time = time.time() - st.session_state.start_time
        st.session_state.total_time_spent += elapsed_time
        st.session_state.start_time = time.time()
        modified_category = umlauts(category)
        if modified_category in to_hide_pages:
            switch_page(modified_category)
        else:
            st.info("Leider haben wir noch keinen Coach für dieses Thema")

    thema_in_category = data[data['Hauptbereich'] == category]['Thema'].tolist()
    icon_in_category = data[data['Hauptbereich'] == category]['emojis'].tolist()
    cols = st.columns(3)

    for i in range(len(thema_in_category)):
        j = (i % 3)
        if cols[j].button(f'{icon_in_category[i]} {thema_in_category[i]}',key=f'{thema_in_category[i]}_{i}'):
            st.session_state.click_count += 1
            elapsed_time = time.time() - st.session_state.start_time
            st.session_state.total_time_spent += elapsed_time
            st.session_state.start_time = time.time()
            modified_thema = umlauts(thema_in_category[i])
            if modified_thema in to_hide_pages:
                switch_page(modified_thema)
            else:
                st.info("Leider haben wir noch keinen Coach für dieses Thema")
        st.write(" ")



#store interaction stats
stt = int(stored_total_time) if stored_total_time else 0
scc = int(stored_click_count) if stored_click_count else 0
user_infos = [[int(st.session_state.total_time_spent)+stt, st.session_state.click_count+scc]]
ws.update(f"AR{user_index}:AS{user_index}", user_infos)