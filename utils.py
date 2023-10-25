import requests
from coach_tools import *
import pandas as pd
import numpy as np
import time
import re
import unicodedata

def init_chat_session():
    st.session_state['generated'] = []
    st.session_state['past'] = []

def init_profile():
    st.session_state['profile'] = None
    st.session_state['selected_hauptbereich'] = None
    st.session_state['selected_thema'] = None
    st.session_state.click_count = 0
    st.session_state.start_time = time.time()
    st.session_state.total_time_spent = 0
    if 'User_index' not in st.session_state:
        st.session_state['User_index'] = None

def load_data(path):
    return pd.read_csv(path, encoding="utf-8")

def on_save_button_click(HK, theme, item):
    st.session_state.click_count += 1
    elapsed_time = time.time() - st.session_state.start_time
    st.session_state.total_time_spent += elapsed_time
    st.session_state.start_time = time.time()

    bookmarks = st.session_state.setdefault('bookmarks', {})
    hk_dict = bookmarks.setdefault(HK, {})
    theme_list = hk_dict.setdefault(theme, [])

    if item not in theme_list:
        theme_list.append(item)
        st.success(f"Saved: {HK, theme, item}")

def load_data(path):
    return pd.read_csv(path)

def keeper(key):
    # Get the updated value of the checkbox and store it in the 'selected_hauptbereich' session_state
    st.session_state['selected_hauptbereich'][key] = st.session_state['_' + key]

def on_remove_button_click(HK, theme, item):
    st.session_state.click_count += 1
    elapsed_time = time.time() - st.session_state.start_time
    st.session_state.total_time_spent += elapsed_time
    st.session_state.start_time = time.time()

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
    """
    Filters the provided data based on a user profile.

    Parameters:
    - data (pd.DataFrame): The data to be filtered.
    - profile (dict): The user profile containing criteria to filter the data.

    Returns:
    - filtered_data (pd.DataFrame): Data that matches the user profile criteria.
    - combined_data (pd.DataFrame): Concatenation of filtered_data and data that did not match the criteria.

    Description:
    The function filters the data based on the user's profile. It creates masks for specific profile items and applies these masks to the data. The resultant data is a combination of rows that match the profile and rows that do not.
    """
    #todo: take argument what profile items to filter

    #String mapping
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

    return filtered_data, combined_data


def scoring_function(data, selected_thema, selected_hauptbereich, profile):
    """
    Assigns scores to the provided data based on selected criteria and user profile.

    Parameters:
    - data (pd.DataFrame): The data to be scored.
    - selected_thema (dict): Selected themes by the user.
    - selected_hauptbereich (dict): Selected main areas by the user.
    - profile (dict): The user profile.

    Returns:
    - sel_thema (list): List of selected themes.
    - scores_other_topics (pd.Series): Normalized scores for other topics.
    - scores (pd.DataFrame): Scores assigned to each row of the data.

    Description:
    The function assigns scores to each row of the data based on how well it matches the selected criteria and the user's profile. The scores are then normalized and returned.
    """
    # Create a new dataframe 'scores' with the same index as 'data' and initialize all values to 0
    scores = pd.DataFrame(0., index=data.index, columns=data.columns)
    max_entries = dict([(d, 0) for d in data.columns])

    sel_hautpbereich = [k for k,v in selected_hauptbereich.items() if v]
    sel_thema = [k for k, v in selected_thema.items() if v]
    selection = sel_hautpbereich+sel_thema

    # iterate over columns and distribute scores
    for column in data.columns:
        max_count = 0
        if column in ["Thema","Hauptbereich","Nebenbereiche"]:
            for idx, value in data[column].items():
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
            for idx, value in data[column].items():
                if isinstance(value, str):
                    column_values = value.split(", ")
                    count = sum([1 for item in column_values if normalize_string(item) == normalize_string(profile[column])])
                    scores.at[idx, column] = count
                    # store maximum # entries
                    if len(column_values) > max_count:
                        max_count = len(column_values)
                        max_entries[column] = max_count
                else:
                    # adding scores for empty variables -> possible: weighted based on user recommendations
                    scores.at[idx, column] = 0.75

    # Normalize the scores per column
    to_normalize = ["Nebenbereiche"]
    for column in to_normalize:
        scores[column] = scores[column] / max_entries[column]

    # normalize 'scores'
    scores["sum"] = scores.sum(axis=1)
    other_topics = scores.loc[~scores.index.isin(sel_thema), "sum"]
    scores_other_topics = other_topics / other_topics.sum()

    return sel_thema, scores_other_topics, scores

def random_feed(df, k=22):
    """
    Randomly selects a subset of rows based on their scores.

    Parameters:
    - df (pd.DataFrame): The data to be sampled.
    - k (int, optional): Number of rows to sample. Default is 24.

    Returns:
    - sampled_series (pd.Series): Randomly sampled rows based on scores.

    Description:
    The function randomly samples a subset of rows from the provided data based on their scores. The probability of a row being selected is proportional to its score.
    """
    p = df.values
    epsilon = 0.000001
    p = p + epsilon
    # Normalize the probabilities to ensure they sum to one
    p /= p.sum()
    # Sample k indices based on probabilities
    sampled_indices = np.random.choice(df.index, size=k, replace=False, p=p)
    # Extract rows corresponding to the sampled indices
    sampled_series = df.loc[sampled_indices]
    return sampled_series


def sort_score(random_thema, data, selected_thema, selected_hauptbereich, k):
    """
    Sorts the provided data based on scores and selected themes.

    Parameters:
    - random_thema (pd.Series): Randomly sampled themes.
    - data (pd.DataFrame): The data to be sorted.
    - selected_thema (list): List of selected themes.
    - k (int): Number of top-scored themes to be included in the final feed.

    Returns:
    - hauptbereich_sorted (pd.DataFrame): Data sorted based on Hauptbereich scores.
    - your_feed (list): Final feed containing selected themes and top-scored items.
    - score_sort_hk

    Description:
    The function sorts the data based on scores. It then constructs a final feed by combining the selected themes and top-scored items.
    """

    s = pd.Series(random_thema)
    # Map 'Thema' values to their 's' scores
    data['scores'] = s
    # Calculate sums of 's'-scores per 'Hauptbereich' category
    sum_scores = data.groupby('Hauptbereich')['scores'].sum()
    # Get group sizes for each 'Hauptbereich'
    group_sizes = data['Hauptbereich'].value_counts()
    # Normalize the sum_scores by group size
    sum_scores = sum_scores / group_sizes
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
    #Remove selected_hauptbereich rows from data
    selected_hk = [key for key, value in selected_hauptbereich.items() if value is True]
    score_sort_hk = hauptbereich_sorted[~hauptbereich_sorted['Hauptbereich'].isin(selected_hk)]

    # Step 2: Select top n score thema from data and add them to your_feed
    n = k - len(selected_thema)
    top_score_thema = score_sort['Thema'].head(n).tolist()
    your_feed += top_score_thema  # Extend the list with top_score_thema elements

    return hauptbereich_sorted, your_feed, score_sort_hk, selected_hk


def umlauts(umlautstring):
    #remove umlauts
    result = re.sub(r'[äöüÄÖÜ]',
           lambda x: {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'}[
               x.group()], umlautstring)
    return result

def normalize_string(s):
    return unicodedata.normalize('NFKD', s).encode('utf-8', 'ignore').decode('utf-8')

def load_text_resources(thema):
    file_path = f"resources/docs/{umlauts(thema)}.txt"
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

            columns = st.columns([0.85, 0.075, 0.075])
            columns[0].markdown(f'<span style="font-size: 20px;">{extract_content_after_number(content_value)}</span>',
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

def extract_content_after_number(text):
    match = re.search(r'\d+\.\s*(.*)', text)
    return match.group(1) if match else None