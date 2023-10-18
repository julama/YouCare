from utils import *
from config import to_hide_pages
from st_pages import add_page_title, hide_pages

# Add page title and hide pages
hide_pages(to_hide_pages)
add_page_title()

if 'profile' not in st.session_state:
    init_profile()

if not st.session_state['profile']:
    st.warning("Bitte erstelle zuerst ein Profil")
    st.stop()
else:
    profile = st.session_state.profile

file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)

# Initialize session state
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = {}  # Initialize bookmarks if not already present

st.session_state.bookmarks
if not st.session_state.bookmarks:
    st.info("Du hast noch keine Inhalte in deiner Sammlung gespeichert")
display_all_saved_items()

