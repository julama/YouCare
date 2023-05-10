from utils import *

#intialize session state:
if 'profile' not in st.session_state:
    init_profile()

if not st.session_state['profile']:
    st.warning("Bitte erstelle zuerst ein Profil")
    st.stop()
else:
    profile = st.session_state.profile
    #filtered_data, combined_data = filter_data_profile(data, profile)

# Load existing text resources
if "text_resources" not in st.session_state:
    st.session_state["text_resources"] = parse_text_file("assets/text_resources/Körperpflege.txt")
Pflege_dicts = st.session_state["text_resources"]

display_bookmarks(Pflege_dicts)