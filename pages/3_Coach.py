import streamlit as st
from utils import display_book,parse_text_file

# Load existing text resources
Pflege_dicts = parse_text_file("assets/text_resources/Körperpflege.txt")

st.title("Mein Coach zum Thema Körperpflege")
display_book(Pflege_dicts)