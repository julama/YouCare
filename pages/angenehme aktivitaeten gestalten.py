from utils import *
from streamlit_extras.switch_page_button import switch_page
#from coach_tools import parse_text_file2
from config import to_hide_pages
from st_pages import hide_pages

# Function to parse the new .txt file format
def parse_new_text_file(file_content):
    sections = {"Zusammenfassung": [], "Herausforderungen": [], "Herausforderungen_Numbers": [], "Hilfestellungen": []}
    current_section = None
    for line in file_content.split('\n'):
        line = line.strip()
        if line in sections:
            current_section = line
        elif current_section:
            if current_section == "Herausforderungen":
                if line and line[0].isdigit():
                    if '.' in line:
                        # This line is a Herausforderung
                        sections[current_section].append(line)
                    else:
                        # This line should contain only numbers (and possibly commas)
                        numbers = [int(n.strip()) for n in line.split(',') if n.strip().isdigit()]
                        sections["Herausforderungen_Numbers"].append(numbers)
                else:
                    # Non-numeric lines in Herausforderungen section are ignored
                    pass
            elif current_section == "Hilfestellungen":
                # Add only lines that start with a digit followed by a period
                if line and line[0].isdigit() and '.' in line:
                    sections[current_section].append(line)
            else:
                sections[current_section].append(line)

    return sections

hide_pages(to_hide_pages)
name = "Angenehme Aktivitäten gestalten"

file_path = "assets/Kategorien_Sortierkriterien.csv"
data = load_data(file_path)
HK = data[data['Thema'].apply(normalize_string) == normalize_string(name)]['Hauptbereich'].iloc[0]

if st.button('Zurück'):
    switch_page("Ratgeber")

# Read the new .txt file
with open(f"resources/docs/{umlauts(name)}.txt", "r", encoding="utf-8") as file:
    text_content = file.read()

if text_content is not None:
    # Parse the new text file
    data = parse_new_text_file(text_content)
    # Display Zusammenfassung section
    if "Zusammenfassung" in data:
        st.header(name)
        for line in data["Zusammenfassung"]:
            st.write(line)

    # Display Herausforderungen section with checkboxes
    selected_indices = []
    if "Herausforderungen" in data:
        st.write("---")
        st.header("Herausforderungen")
        for i, herausforderung in enumerate(data["Herausforderungen"]):
            if st.checkbox(herausforderung, key=f"herausforderung_{i}"):
                selected_indices.append(i)

    st.write("---")
    st.header("Tipps & Anregungen")

    # Aggregate Hilfestellungen from selected Herausforderungen
    aggregated_priority_indices = []
    for index in selected_indices:
        aggregated_priority_indices.extend(data["Herausforderungen_Numbers"][index])
    aggregated_priority_indices = list(set(aggregated_priority_indices))  # Remove duplicates

    # Sort Hilfestellungen based on the aggregated priority indices
    priority_hilfestellungen = [data["Hilfestellungen"][i-1] for i in aggregated_priority_indices if i-1 < len(data["Hilfestellungen"])]
    other_hilfestellungen = [h for h in data["Hilfestellungen"] if h not in priority_hilfestellungen]
    sorted_hilfestellungen = priority_hilfestellungen + other_hilfestellungen

    # Display Hilfestellungen
    for i, content_value in enumerate(sorted_hilfestellungen):
        expanded = True
        with st.expander(f"Tipp {i+1}", expanded=expanded):
            columns = st.columns([0.85, 0.075, 0.075])
            columns[0].markdown(f'<span style="font-size: 20px;">{extract_content_after_number(content_value)}</span>', unsafe_allow_html=True)

            save_key = f"{name} {i}"
            if columns[1].button("💾", key=f"save_test_{i}"):
                on_save_button_click(HK, name, i)