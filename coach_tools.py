import streamlit as st

def parse_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    sections = content.split('@')[1:]
    parsed_data = {}

    for section in sections:
        lines = section.strip().split('\n')
        section_title = lines.pop(0).strip()
        topic = lines.pop(0).strip()

        if topic not in parsed_data:
            parsed_data[topic] = {}

        if any('- ' in line for line in lines):
            section_dict = {}
            section_counter = 1
            section_text = ''
            for line in lines:
                if '- ' in line:
                    if section_text:
                        section_name = f"{section_title}_{section_counter}"
                        section_dict[section_name] = section_text.strip()
                        section_counter += 1
                    section_text = line.replace('- ', '')
                else:
                    section_text += f' {line}'
            section_name = f"{section_title}_{section_counter}"
            section_dict[section_name] = section_text.strip()
            parsed_data[topic][section_title] = section_dict
        else:
            parsed_data[topic][section_title] = ' '.join(lines)

    return parsed_data

# Function to parse the text file
def parse_text_file2(file_content):
    sections = ["Zusammenfassung", "Herausforderungen", "Hilfestellungen"]
    section_data = {}

    current_section = None
    lines = file_content.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        if line in sections:
            current_section = line
            section_data[current_section] = []
        elif current_section:
            section_data[current_section].append(line)

    return section_data
def display_book(parsed_data):
    # Sidebar for section selection
    st.sidebar.title("Kapitel")
    section_names = list(parsed_data.keys())
    current_section = st.sidebar.selectbox("Select a section", section_names)

    # Sidebar for topic selection within the selected section
    st.sidebar.title("Topics")
    topic_names = list(parsed_data[current_section].keys())
    current_topic = st.sidebar.selectbox("Select a topic", topic_names)

    # Display the content of the selected topic
    st.title(f"{current_section} {current_topic}")
    content = parsed_data[current_section][current_topic]

    if isinstance(content, dict):
        for subsection_title, subsection_content in content.items():
            with st.expander(f"{subsection_title[:-2]}", expanded=False):
                columns = st.columns([0.85, 0.075, 0.075])
                columns[0].markdown(f'<span style="font-size: 20px;">{subsection_content}</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span style="font-size: 20px;">{content}</span>', unsafe_allow_html=True)