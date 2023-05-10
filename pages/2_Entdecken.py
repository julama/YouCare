from utils import *
#from notion_client import Client
import streamlit.components.v1 as components
from assets.html import html_string
from coach_tools import parse_text_file

# Load the CSV file
#st.cache_resource
def load_data(path):
    return pd.read_csv(path)

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
    filtered_data, combined_data = filter_data_profile(data, profile)

selected_thema = st.session_state['selected_thema']
selected_hauptbereich = st.session_state['selected_hauptbereich']

#data

# Score Sortierkriterien based on profile and selection
sel_thema, scores_other_topics = scoring_function(data, selected_thema, selected_hauptbereich, profile)
random_thema = random_feed(scores_other_topics, k=6)

# Display the scrollable feed of textboxes
st.header("Entecke Inhalte")
file_path = 'assets/text_resources/Wohnanpassung & Hilfsmittel.txt'
All_answers = process_file(file_path)

# Load existing text resources
if "text_resources" not in st.session_state:
    st.session_state["text_resources"] = parse_text_file("assets/text_resources/Körperpflege.txt")
Pflege_dicts = st.session_state["text_resources"]

# Warn for unavailable data
for t in sel_thema:
    if t != "Körperpflege & Toilette":
        st.info(f"Für {t} haben wir noch keine passenden Infos")


if "Körperpflege & Toilette" in sel_thema:
    display_feed(Pflege_dicts)

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


