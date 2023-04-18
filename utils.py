import requests
import streamlit as st
import pandas as pd
import numpy as np

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

        if section_title.lower() == "summary":
            parsed_data[topic][section_title] = ' '.join(lines)
        else:
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

def display_data(parsed_data, max_expanders_per_section=3):
    for topic, sections in parsed_data.items():
        for section_title, content in sections.items():
            section_title_with_topic = f"{section_title}: {topic[:-1]}"
            expander_counter = 0
            if isinstance(content, dict):
                all_subsection_contents = ""
                for idx, sub_cont in enumerate(content.items()):
                    subsection_title, subsection_content = sub_cont
                    all_subsection_contents += f"**{subsection_title[:-2]} {idx+1}**\n\n{subsection_content}\n\n"
                if expander_counter < max_expanders_per_section:
                    with st.expander(section_title_with_topic, expanded=False):
                        columns = st.columns([0.85, 0.075, 0.075])
                        columns[0].markdown(f'<span style="font-size: 20px;">{all_subsection_contents}</span>', unsafe_allow_html=True)
                        columns[1].button("💾", key=f"like_{section_title_with_topic}")
                    expander_counter += 1
            else:
                if expander_counter < max_expanders_per_section:
                    with st.expander(section_title_with_topic, expanded=False):
                        columns = st.columns([0.85, 0.075, 0.075])
                        columns[0].markdown(f'<span style="font-size: 20px;">{content}</span>', unsafe_allow_html=True)
                        columns[1].button("💾", key=f"like_{section_title_with_topic}")
                    expander_counter += 1

@st.cache_data
def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    lines = content.split('\n')
    paragraphs = [line.strip().replace('\xad', '') for line in lines if line.strip()]
    return paragraphs

def load_data_notion(database_id):
    # Get the list of pages in the database
    pages = []
    page_cursor = None
    while True:
        results = notion.databases.query(
            **{
                "database_id": database_id,
                "filter": {},
                "start_cursor": page_cursor,
            }
        ).get("results")
        pages.extend(results)
        page_cursor = notion.get_next_cursor()
        if not page_cursor:
            break

    # Convert the list of pages to a pandas DataFrame
    data = []
    for page in pages:
        row = {}
        for prop, value in page["properties"].items():
            if value["type"] == "title":
                row[prop] = value["title"][0]["text"]["content"]
            elif value["type"] == "rich_text":
                row[prop] = value["rich_text"][0]["text"]["content"]
            elif value["type"] == "number":
                row[prop] = value["number"]
            # Add more property types if needed
        data.append(row)

    return pd.DataFrame(data)

def query(texts, api_url, headers):
    response = requests.post(api_url, headers=headers, json={"inputs": texts})
    result = response.json()
    if isinstance(result, list):
        return result
    elif list(result.keys())[0] == "error":
        st.info('Bitte habe einen Moment Geduld. Der Coach wird geladen')

def get_text():
    input_text = st.text_input(f"", "Schreibe hier deine Frage", key="input")
    return input_text

def init_chat_session():
    st.session_state['generated'] = []
    st.session_state['past'] = []

def init_profile():
    st.session_state['profile'] = []

def custom_button(item, key, is_selected):
    button_css = f"""<style>
        .{key} {{
            border-radius: 25px;
            background-color: {'#f63366' if is_selected else '#ffffff'};
            color: {'white' if is_selected else 'black'};
            padding: 0.25em 0.5em;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border: 2px solid #f63366;
        }}
    </style>"""

    button_js = f"""<script>
        function handleClick{key}() {{
            var button = document.getElementById("{key}");
            var is_selected = button.classList.contains("selected");
            button.style.backgroundColor = is_selected ? "#ffffff" : "#f63366";
            button.style.color = is_selected ? "black" : "white";
            button.classList.toggle("selected");
        }}
    </script>"""

    return f"{button_css}{button_js}<button class='{key}' id='{key}' onclick='handleClick{key}()'>{item}</button>"


def filter_data_profile(data, profile):
    #todo: take argument what profile items to filter

    # String mapping
    wohnsituation = profile["Wohnsituation (!)"]
    diagnose = profile["Diagnose (!)"]
    Demenzstadium = profile["Demenzstadium (!)"]

    # Create a mask for each column to check if the value matches the user profile or if the cell is empty
    #todo: For profile_item in profile do:
    mask_wohnsituation = data["Wohnsituation (!)"]\
        .apply(lambda x: wohnsituation in x.split(", ") if isinstance(x, str) else True)
    mask_diagnose = data["Diagnose (!)"]\
        .apply(lambda x: diagnose in x.split(", ") if isinstance(x, str) else True)
    mask_demenzstadium = data["Demenzstadium (!)"]\
        .apply(lambda x: Demenzstadium in x.split(", ") if isinstance(x, str) else True)

    # Filter the data using the masks
    filtered_data = data[mask_wohnsituation & mask_diagnose & mask_demenzstadium]
    # Apply the inverse mask to the original data
    inverse_mask_data = data[~(mask_wohnsituation & mask_diagnose & mask_demenzstadium)]
    # Concatenate filtered_data and inverse_mask_data
    combined_data = pd.concat([filtered_data, inverse_mask_data], ignore_index=True)

    #todo: filter data sequential. e.g. if stadium schwer-> remove mittel+ leicht

    return filtered_data, combined_data


def scoring_function(data, selected_thema, selected_hauptbereich, profile):
    # Create a new dataframe 'scores' with the same index as 'data' and initialize all values to 0
    scores = pd.DataFrame(0, index=data["Thema"], columns=data.columns)
    data = data.set_index(data["Thema"])
    max_entries = dict([(d, 0) for d in data.columns])

    sel_hautpbereich = [k for k,v in selected_hauptbereich.items() if v]
    sel_thema = [k for k, v in selected_thema.items() if v]
    selection = sel_hautpbereich+sel_thema

    # iterate over columns an distribute scores
    for column in data.columns:
        max_count = 0
        if column in ["Thema","Hauptbereich","Nebenbereiche"]:
            for idx, value in data[column].iteritems():
                if isinstance(value, str):
                    column_values = value.split(",")
                    count = sum([1 for item in column_values if item.strip() in selection])
                    scores.at[idx, column] = count
                    # store maximum # entries
                    if len(column_values) > max_count:
                        max_count = len(column_values)
                        max_entries[column] = max_count

        elif column in profile.keys():
            max_count = 0
            for idx, value in data[column].iteritems():
                if isinstance(value, str):
                    column_values = value.split(", ")
                    count = sum([1 for item in column_values if item == profile[column]])
                    scores.at[idx, column] = count
                    # store maximum # entries
                    if len(column_values) > max_count:
                        max_count = len(column_values)
                        max_entries[column] = max_count

    # Normalize the scores per column
    to_normalize = ["Nebenbereiche"]
    for column in to_normalize:
        scores[column] = scores[column] / max_entries[column]

    # normalize 'scores'
    scores["sum"] = scores.sum(axis=1)
    other_topics = scores.loc[~scores.index.isin(sel_thema), "sum"]
    scores_other_topics = other_topics / other_topics.sum()

    # Change selected Thema to propability 1
    selected = [k for k, v in selected_thema.items() if v]

    return selected, scores_other_topics

def random_feed(p, k=5):
    np.random.seed(42)
    sel_other_topics = np.random.choice(p.index, size=k, replace=False, p=p)

    return sel_other_topics

def display_book(parsed_data):
    # Sidebar for section selection
    st.sidebar.title("Sections")
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


# # Create a container to hold the text output
# with st.container():
#     # Add custom CSS to create a box-like appearance
#     st.markdown("""
#         <style>
#             .box {
#                 border: 1px;
#                 border-radius: 10px;
#                 padding: 20px;
#                 background-color: #2B5071;
#                 color: white;
#             }
#         </style>
#     """, unsafe_allow_html=True)
#
#     # Display the text output inside a div with the 'box' class
#     st.markdown(f"<div class='box'>{random_recomendation}</div>", unsafe_allow_html=True)
