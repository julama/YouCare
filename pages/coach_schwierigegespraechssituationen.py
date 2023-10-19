from utils import *
from streamlit_extras.switch_page_button import switch_page
from coach_tools import parse_text_file2
from config import to_hide_pages
from st_pages import hide_pages

hide_pages(to_hide_pages)
name = "Schwierige Gesprächssituationen"

file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)
HK = data[data['Thema'].apply(normalize_string) == name]['Hauptbereich'].iloc[0]

if st.button('Zurück'):
        switch_page("coach")

import streamlit as st

# Read the .txt file
with open(f"resources/docs/{name}.txt", "r", encoding="utf-8") as file:
    text_content = file.read()

if text_content is not None:
    file_content = text_content

    # Parse the text file
    data = parse_text_file2(file_content)

    # Display Zusammenfassung section
    if "Zusammenfassung" in data:
        st.header(name)
        for line in data["Zusammenfassung"]:
            st.write(line)

    # Display Herausforderungen section
    if "Herausforderungen" in data:
        st.write("---")
        st.header("Herausforderungen")
        for i, line in enumerate(data["Herausforderungen"], 1):
            st.write(f"{line}")

    st.write("---")
    st.header("Tipps & Anregungen")
    for i, content_value in enumerate(data["Hilfestellungen"]):
        expanded = True

        with st.expander(f"Tipp {i+1}", expanded=expanded):
            columns = st.columns([0.85, 0.075, 0.075])
            columns[0].markdown(f'<span style="font-size: 20px;">{content_value[2:]}</span>',
                                unsafe_allow_html=True)

            save_key = f"{name} {i}"
            if columns[1].button("💾", key=f"save_test_{i}"):
                on_save_button_click(HK, name, i)



