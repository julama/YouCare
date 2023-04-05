import streamlit as st
import pandas as pd
import random
from utils import *

# Load the CSV file
st.cache_resource
def load_data(path):
    return pd.read_csv(path)

file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)

# Get unique values from "Thema" and "Hauptbereich" columns
unique_thema = data["Thema"].dropna().unique()
unique_hauptbereich = data["Hauptbereich"].dropna().unique()

# Select 4 random items from each column
random.seed(42)
random_thema = random.sample(list(unique_thema), 4)
random_hauptbereich = random.sample(list(unique_hauptbereich), 4)

selected_thema = st.session_state.get("selected_thema", set())
selected_hauptbereich = st.session_state.get("selected_hauptbereich", set())

# Display checkboxes with random items
st.header("Meine Themen")

# Thema
columns = st.columns(4)
for idx, item in enumerate(random_thema):
    key = f"thema_{idx}"
    is_selected = key in selected_thema
    if columns[idx].checkbox(item, key=key, value=is_selected):
        selected_thema.add(key)
    else:
        selected_thema.discard(key)

# Hauptbereich
columns = st.columns(4)
for idx, item in enumerate(random_hauptbereich):
    key = f"hauptbereich_{idx}"
    is_selected = key in selected_hauptbereich
    if columns[idx].checkbox(item, key=key, value=is_selected):
        selected_hauptbereich.add(key)
    else:
        selected_hauptbereich.discard(key)

# Display the search field
search = st.text_input("Verfeinere deine Suche mit Stichworten oder einer Frage", value="", key="search_field")
search_icon = '<i class="fas fa-search"></i>'
st.markdown(search_icon, unsafe_allow_html=True)

# Display the scrollable feed of textboxes
st.header("Feed")
file_path = 'assets/text_resources/Wohnanpassung & Hilfsmittel.txt'
All_answers = process_file(file_path)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

for idx, answer in enumerate(All_answers):
    expander_text = f'{random_thema[idx % len(random_thema)]}'
    with st.expander(expander_text, expanded=False):
        columns = st.columns([0.85, 0.075, 0.075])
        columns[0].markdown(f'<span style="font-size: 20px;">{answer}</span>', unsafe_allow_html=True)
        columns[1].button("👍", key=f"like_{answer}")
        columns[2].button("👎", key=f"dislike_{answer}")

