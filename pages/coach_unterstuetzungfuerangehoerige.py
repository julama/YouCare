from utils import *
from st_pages import Page, show_pages, add_page_title, Section, hide_pages
from streamlit_extras.switch_page_button import switch_page
from coach_tools import parse_text_file2
from config import to_hide_pages, emoji_dict
from st_pages import add_page_title, hide_pages
hide_pages(to_hide_pages)

name = "Unterstützung für Angehörige"
file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)
emoji_values = list(emoji_dict.values())
data['emojis'] = emoji_values

if st.button('Zurück'):
        switch_page("Ratgeber")

import streamlit as st

# Read the .txt file
with open(f"resources/docs/HK/{name}.txt", "r", encoding="utf-8") as file:
    text_content = file.read()

if text_content is not None:
    file_content = text_content

    # Parse the text file
    textfile = parse_text_file2(file_content)

    # Display Zusammenfassung section
    if "Zusammenfassung" in textfile:
        st.header(name)
        for line in textfile["Zusammenfassung"]:
            st.write(line)

    st.write("---")
    st.subheader(f"Entdecke Themen in \"{name}\"")

    #display all Themas of Hauptkategorie
    thema_in_category = data[data['Hauptbereich'] == name]['Thema'].tolist()
    icon_in_category = data[data['Hauptbereich'] == name]['emojis'].tolist()
    cols = st.columns(3)

    for i in range(len(thema_in_category)):
        j = (i % 3)
        if cols[j].button(f'{icon_in_category[i]} {thema_in_category[i]}', key=f'{thema_in_category[i]}_{i}'):
            modified_thema = umlauts(thema_in_category[i])
            if modified_thema in to_hide_pages:
                switch_page(modified_thema)
            else:
                st.info("Leider haben wir noch keinen Coach für dieses Thema")
        st.write(" ")


