import requests
import streamlit as st
from coach_tools import *
import pandas as pd
import numpy as np
import nltk
from streamlit_modal import Modal
import re
import unicodedata
import streamlit.components.v1 as components
nltk.download('punkt')

def init_chat_session():
    st.session_state['generated'] = []
    st.session_state['past'] = []

def init_profile():
    st.session_state['profile'] = None
    st.session_state['selected_hauptbereich'] = None
    st.session_state['selected_thema'] = None

def load_data(path):
    return pd.read_csv(path, encoding="utf-8")

def on_save_button_click(HK, theme, item):
    bookmarks = st.session_state.setdefault('bookmarks', {})
    hk_dict = bookmarks.setdefault(HK, {})
    theme_list = hk_dict.setdefault(theme, [])

    if item not in theme_list:
        theme_list.append(item)
        st.success(f"Saved: {HK, theme, item}")


def on_remove_button_click(HK, theme, item):
    bookmarks = st.session_state.get('bookmarks', {})

    if HK in bookmarks and theme in bookmarks[HK]:
        theme_list = bookmarks[HK][theme]

        if item in theme_list:
            theme_list.remove(item)
            #st.success(f"Removed: {HK, theme, item}")

            # Check if the theme list is empty and remove the theme if it is
            if not theme_list:
                del bookmarks[HK][theme]
                #st.success(f"Theme {theme} has been removed as it is empty.")

            # Check if the HK is empty (no themes in the HK) and remove HK if it is
            if not bookmarks[HK]:
                del bookmarks[HK]
                #st.success(f"Hauptkategorie {HK} has been removed as it is empty.")
        else:
            st.warning(f"Item {item} not found in the list.")
    else:
        st.warning(f"Theme {theme} or Hauptkategorie {HK} not found in bookmarks.")

    st.rerun()


def create_modal(key, button_label, title, topic_summaries, content_section):
    modal = Modal(key=key, title=title)
    open_modal = st.button(button_label)
    if open_modal:
        modal.open()
    if modal.is_open():
        with modal.container():
            content = topic_summaries[content_section]
            if isinstance(content, dict):
                content = " ".join([value for value in content.values()])
            st.write(content)


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

def display_bookmarks(parsed_data, max_expanders_per_section=20):
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
                    #st.write(section_title_with_subsection)
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


def display_bookmarks2(parsed_data, max_expanders_per_section=20):
    if 'bookmarks' not in st.session_state:
        st.session_state['bookmarks'] = {}

    bookmarks = st.session_state['bookmarks']

    # Grouping bookmarks by topics
    grouped_bookmarks = {}
    for bookmark in bookmarks:
        topic, section = bookmark.split(":")[0], bookmark.split(":")[1]
        if topic not in grouped_bookmarks:
            grouped_bookmarks[topic] = []
        grouped_bookmarks[topic].append(section)

    # Displaying bookmarks by topic
    for topic, sections in parsed_data.items():
        if topic in grouped_bookmarks:
            st.header(topic[:-1])  # Display the topic name
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
                                    columns[0].markdown(f'<span style="font-size: 20px;">{subsection_content}</span>', unsafe_allow_html=True)
                                    if columns[1].button("💾", key=f"like_{section_title_with_subsection}"):
                                        on_save_button_click(section_title_with_subsection)
                                expander_counter += 1
                else:
                    # Check if the item is in bookmarks
                    if section_title_with_topic in bookmarks:
                        if expander_counter < max_expanders_per_section:
                            with st.expander(section_title_with_topic, expanded=False):
                                columns = st.columns([0.85, 0.075, 0.075])
                                columns[0].markdown(f'<span style="font-size: 20px;">{content}</span>', unsafe_allow_html=True)
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

def get_selected_thema(dictionary):
    return [k for k, v in dictionary.items() if v is True]


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

    #todo: filter data sequential. e.g. if stadium mittel-> remove leicht

    return filtered_data, combined_data


def scoring_function(data, selected_thema, selected_hauptbereich, profile):
    # Create a new dataframe 'scores' with the same index as 'data' and initialize all values to 0
    scores = pd.DataFrame(0, index=data.index, columns=data.columns)
    max_entries = dict([(d, 0) for d in data.columns])

    sel_hautpbereich = [k for k,v in selected_hauptbereich.items() if v]
    sel_thema = [k for k, v in selected_thema.items() if v]
    selection = sel_hautpbereich+sel_thema

    # iterate over columns and distribute scores
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

    #selected = [k for k, v in selected_thema.items() if v]

    return sel_thema, scores_other_topics

def random_feed(df, k=24):
    p = df.values

    epsilon = 0.0001
    p = p + epsilon

    # Normalize the probabilities to ensure they sum to one
    p /= p.sum()

    # Sample k indices based on probabilities
    sampled_indices = np.random.choice(df.index, size=k, replace=False, p=p)

    # Extract rows corresponding to the sampled indices
    sampled_series = df.loc[sampled_indices]

    return sampled_series


def sort_score(random_thema, data, selected_thema, k):
    s = pd.Series(random_thema)
    # Map 'Thema' values to their 's' scores
    data['scores'] = s
    # Calculate sums of 's'-scores per 'Hauptbereich' category
    sum_scores = data.groupby('Hauptbereich')['scores'].sum()
    # Map 'Hauptbereich' values to their sum_scores
    data['Hauptbereich_scores'] = data['Hauptbereich'].map(sum_scores)
    # Sort df according to 'Hauptbereich' scores and 'Thema' scores within each 'Hauptbereich'
    hauptbereich_sorted = data.copy()
    hauptbereich_sorted.sort_values(['Hauptbereich_scores', 'scores'], ascending=[False, False], inplace=True)
    data.sort_values(['scores'], ascending=[False], inplace=True)
    score_sort = data

    # Step 0: Define your_feed and add selected_thema to the beginning
    your_feed = selected_thema  # Start with selected_thema

    # Step 1: Remove selected_thema rows from data
    score_sort = score_sort[~score_sort['Thema'].isin(selected_thema)]

    # Step 2: Select top n score thema from data and add them to your_feed
    n = k - len(selected_thema)
    top_score_thema = score_sort['Thema'].head(n).tolist()
    your_feed += top_score_thema  # Extend the list with top_score_thema elements

    return hauptbereich_sorted, your_feed


def umlauts(umlautstring):
    #remove umlauts
    result = re.sub(r'[äöüÄÖÜ]',
           lambda x: {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'}[
               x.group()], umlautstring)
    return result

def normalize_string(s):
    return unicodedata.normalize('NFKD', s).encode('utf-8', 'ignore').decode('utf-8')

def load_text_resources(thema):
    file_path = f"resources/docs/{thema}.txt"
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return None


def display_thema_items(thema, items, thema_text, category):
    data = parse_text_file2(thema_text)

    sorted_items = sorted(items)
    for item in sorted_items:
        item_index = item
        if "Hilfestellungen" in data and 0 <= item_index < len(data["Hilfestellungen"]):
            content_value = data["Hilfestellungen"][item_index]
            #st.write(content_value)
            #if st.button("🗑️", key=f"save_{thema}_{item}"):
                #on_remove_button_click(category, thema, item)

            columns = st.columns([0.85, 0.075, 0.075])
            columns[0].markdown(f'<span style="font-size: 20px;">{content_value}</span>',
                                unsafe_allow_html=True)

            if columns[1].button("🗑️", key=f"remove_{thema}_{item}"):
                on_remove_button_click(category, thema, item)


def display_all_saved_items():
    if 'bookmarks' not in st.session_state:
        st.warning("No bookmarks found.")
        return

    for category, category_data in st.session_state.bookmarks.items():
        st.title(category)
        for thema, items in category_data.items():
            st.subheader(thema)
            with st.expander(f"Gespeicherten Tipps zum Thema {thema}", expanded=False):
                thema_text = load_text_resources(thema)
                if thema_text:
                    display_thema_items(thema, items, thema_text, category)