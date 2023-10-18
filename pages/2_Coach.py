from utils import *
from streamlit_extras.switch_page_button import switch_page
from config import to_hide_pages, emoji_dict
from st_pages import add_page_title, hide_pages
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

st.write(" ")
st.write(" ")

selected_thema = st.session_state['selected_thema']
selected_hauptbereich = st.session_state['selected_hauptbereich']

# Score Sortierkriterien based on profile and selection
filtered_data, combined_data = filter_data_profile(data, profile)
sel_thema, scores_other_topics, scores = scoring_function(data, selected_thema, selected_hauptbereich, profile)
random_thema = random_feed(scores_other_topics)
sel_thema_values = get_selected_thema(selected_thema)
data_sorted, your_feed = sort_score(random_thema, data, sel_thema_values, 6)

# your_feed
st.header('Deine Themen')
cols = st.columns(3)
for i in range(len(your_feed)):
    j = (i % 3)
    if cols[j].button(f"{emoji_dict[your_feed[i]]} {your_feed[i]}", key=f'feed_{i}'):
        modified_string = umlauts(your_feed[i])
        if modified_string in to_hide_pages:
            switch_page(modified_string)
        else:
            st.info("Leider haben wir noch keinen Coach für dieses Thema")

## Empfehlungen Section
st.write("---")
e1, section_title, e12 = st.columns([10,8,10])
st.header('Alle Themen im Überblick')

categories = data_sorted['Hauptbereich'].unique()
st.write(" ")
for category in categories:
    cat_title, cat_info = st.columns([1,8])
    with cat_info:
        st.write(" ")
        st.subheader(category)
    with cat_title:
        st.write(" ")
    if cat_title.button('ℹ️', key=f'{category}_info'):
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
            modified_thema = umlauts(thema_in_category[i])
            if modified_thema in to_hide_pages:
                switch_page(modified_thema)
            else:
                st.info("Leider haben wir noch keinen Coach für dieses Thema")
        st.write(" ")



