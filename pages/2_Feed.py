import streamlit as st
from utils import *
#from notion_client import Client
import streamlit.components.v1 as components
from assets.html import html_string

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

# Load profile and filter data
if "profile" not in st.session_state:
    st.warning("Bitte erstelle zuerst ein Profil")
    st.stop()
else:
    profile = st.session_state.profile
filtered_data, combined_data = filter_data_profile(data, profile)

# Get unique values from "Thema" and "Hauptbereich" columns
unique_thema_filtered = filtered_data["Thema"].unique()
unique_hauptbereich_filtered = filtered_data["Hauptbereich"].unique()

# initalize selected Hauptbereich
if 'selected_hauptbereich' not in st.session_state:
    pass
# initalize selected Thema
if 'selected_thema' not in st.session_state:
    pass

# Hauptbereich Checkbox
columns = st.columns(2)
selected_hauptbereich = dict([(i,False) for i in unique_hauptbereich_filtered])
for idx, item in enumerate(unique_hauptbereich_filtered):
    if isinstance(item, str):
        column_idx = idx % 2
        selected_hauptbereich[item] = columns[column_idx].checkbox(item)


## Filter Thema based on selection
hauptbereich_keys = [k for k, v in selected_hauptbereich.items() if v]
mask_thema = data[data["Hauptbereich"].isin(hauptbereich_keys)]
unique_thema_filtered = mask_thema["Thema"].dropna().unique()

hauptbereich_string = " und ".join(hauptbereich_keys)
if hauptbereich_keys:
    st.header(f"Beim Thema {hauptbereich_string} beschäftigen mich:")

# Themen Checkbox
columns = st.columns(2)
selected_thema = dict([(i,False) for i in unique_thema_filtered])
for idx, item in enumerate(unique_thema_filtered):
    if isinstance(item, str):
        column_idx = idx % 2
        selected_thema[item] = columns[column_idx].checkbox(item)

# Display the search field
search = st.text_input("Verfeinere deine Suche mit Stichworten oder einer Frage", value="", key="search_field")
search_icon = '<i class="fas fa-search"></i>'
st.markdown(search_icon, unsafe_allow_html=True)

# Score Sortierkriterien based on profile and selection
sel_thema, scores_other_topics = scoring_function(data, selected_thema, selected_hauptbereich, profile)
random_thema = random_feed(scores_other_topics, k=6)

# Display the scrollable feed of textboxes
st.header("Feed")
file_path = 'assets/text_resources/Wohnanpassung & Hilfsmittel.txt'
All_answers = process_file(file_path)

# Load existing text resources
Pflege_dicts = parse_text_file("assets/text_resources/Körperpflege.txt")
# Warn for unavailable data
for t in sel_thema:
    if t != "Körperpflege & Toilette":
        st.info(f"Für {t} haben wir noch keine passenden Infos")
if "Körperpflege & Toilette" in sel_thema:
    display_data(Pflege_dicts)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("assets/style.css")

st.subheader("Entecke weitere Themen:")
for thema in random_thema:
    answer = "Für dieses Thema haben wir noch keine passenden Infos"

    # Replace the placeholders in the html_string with the desired values
    formatted_html_string = html_string.format(thema, "solutions")
    # Use the formatted_html_string with the components.html function
    components.html(formatted_html_string, height=0, width=0)

    with st.expander(thema, expanded=False):
        columns = st.columns([0.85, 0.075, 0.075])
        columns[0].markdown(f'<span style="font-size: 20px;">{answer}</span>', unsafe_allow_html=True)
        #columns[1].button("👍", key=f"like_{answer}")
        #columns[2].button("👎", key=f"dislike_{answer}")


