import gspread as gs
from utils import *
from config import to_hide_pages
from st_pages import add_page_title, hide_pages, show_pages_from_config
import json

# Add page title and hide pages
show_pages_from_config()
hide_pages(to_hide_pages)
add_page_title()

if 'profile' not in st.session_state:
    init_profile()

if not st.session_state['profile']:
    st.warning("Bitte erstelle zuerst ein Profil")
    st.stop()
else:
    profile = st.session_state.profile

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

file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)

# Initialize session state
if "bookmarks" not in st.session_state:
    serialized_data = ws.acell(f"AT{user_index}").value
    retrieved_data = json.loads(serialized_data)
    st.session_state.bookmarks = retrieved_data if retrieved_data else {}  # Initialize bookmarks if not already present

#store interaction stats in db
stt = int(stored_total_time) if stored_total_time else 0
scc = int(stored_click_count) if stored_click_count else 0
user_infos = [[int(st.session_state.total_time_spent)+stt, st.session_state.click_count+scc]]
ws.update(f"AR{user_index}:AS{user_index}", user_infos)

#store bookmarks in db
serialized_data = json.dumps(st.session_state.bookmarks)
ws.update_acell(f"AT{user_index}", serialized_data)

if not st.session_state.bookmarks:
    st.info("Du hast noch keine Inhalte in deiner Sammlung gespeichert")
display_all_saved_items()

