import requests
import streamlit as st
import pandas as pd
import numpy as np
import nltk
nltk.download('punkt')


def on_save_button_click(section_title):
    if 'bookmarks' not in st.session_state:
        st.session_state['bookmarks'] = {}
    st.session_state['bookmarks'][section_title] = True
    st.success(f"Saved: {section_title}")


def display_feed(parsed_data, max_expanders_per_section=3):
    for topic, sections in parsed_data.items():
        for section_title, content in sections.items():
            section_title_with_topic = f"{topic[:-1]}: {section_title}"
            expander_counter = 0
            if isinstance(content, dict):
                for idx, sub_cont in enumerate(content.items()):
                    subsection_title, subsection_content = sub_cont
                    section_title_with_subsection = f"{section_title_with_topic} - {subsection_title}"

                    # Count the number of sentences in the subsection_content
                    num_sentences = len(nltk.sent_tokenize(subsection_content))

                    # Set expanded to True if num_sentences <= 2, else set it to False
                    expanded = num_sentences <= 2

                    if expander_counter < max_expanders_per_section:
                        with st.expander(section_title_with_subsection, expanded=expanded):
                            columns = st.columns([0.85, 0.075, 0.075])
                            columns[0].markdown(f'<span style="font-size: 20px;">{subsection_content}</span>',
                                                unsafe_allow_html=True)
                            if columns[1].button("💾", key=f"like_{section_title_with_subsection}"):
                                on_save_button_click(section_title_with_subsection)
                        expander_counter += 1
            else:
                if expander_counter < max_expanders_per_section:
                    with st.expander(section_title_with_topic, expanded=False):
                        columns = st.columns([0.85, 0.075, 0.075])
                        columns[0].markdown(f'<span style="font-size: 20px;">{content}</span>', unsafe_allow_html=True)
                        if columns[1].button("💾", key=f"like_{section_title_with_topic}"):
                            on_save_button_click(section_title_with_topic)
                    expander_counter += 1


def display_bookmarks(parsed_data, max_expanders_per_section=3):
    if 'bookmarks' not in st.session_state:
        st.session_state['bookmarks'] = {}

    bookmarks = st.session_state['bookmarks']

    for topic, sections in parsed_data.items():
        for section_title, content in sections.items():
            section_title_with_topic = f"{topic[:-1]}: {section_title}"
            expander_counter = 0
            if isinstance(content, dict):
                for idx, sub_cont in enumerate(content.items()):
                    subsection_title, subsection_content = sub_cont
                    section_title_with_subsection = f"{section_title_with_topic} - {subsection_title}"

                    # Check if the item is in bookmarks
                    if section_title_with_subsection in bookmarks:

                        # Count the number of sentences in the subsection_content
                        num_sentences = len(nltk.sent_tokenize(subsection_content))

                        # Set expanded to True if num_sentences <= 2, else set it to False
                        expanded = num_sentences <= 2

                        if expander_counter < max_expanders_per_section:
                            with st.expander(section_title_with_subsection, expanded=expanded):
                                columns = st.columns([0.85, 0.075, 0.075])
                                columns[0].markdown(f'<span style="font-size: 20px;">{subsection_content}</span>',
                                                    unsafe_allow_html=True)
                                if columns[1].button("💾", key=f"like_{section_title_with_subsection}"):
                                    on_save_button_click(section_title_with_subsection)
                            expander_counter += 1
            else:
                # Check if the item is in bookmarks
                if section_title_with_topic in bookmarks:
                    if expander_counter < max_expanders_per_section:
                        with st.expander(section_title_with_topic, expanded=False):
                            columns = st.columns([0.85, 0.075, 0.075])
                            columns[0].markdown(f'<span style="font-size: 20px;">{content}</span>',
                                                unsafe_allow_html=True)
                            if columns[1].button("💾", key=f"like_{section_title_with_topic}"):
                                on_save_button_click(section_title_with_topic)
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
    st.session_state['profile'] = None
    st.session_state['selected_hauptbereich'] = None
    st.session_state['selected_thema'] = None

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
    scores = pd.DataFrame(0, index=data.index, columns=data.columns)
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
