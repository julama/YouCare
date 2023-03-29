import streamlit as st
from streamlit_chat import message
import pandas as pd
import torch
from sentence_transformers.util import semantic_search
from random import choice
from utils import *

#intialize session state:
if 'generated' not in st.session_state:
    init_chat_session()


st.title("Interaktiver Coach")

# Load the pre-defined CSV file
file_path = "assets/Kategorien_Sortierkriterien.csv"
data = pd.read_csv(file_path)

st.write("### Was belastet dich gerade?")

st.info("Es sind erst Antworten für 'Demenzstadium: schwer' & 'Alltag aktiv gestalten' hinterlegt")


# Select a value from the Demenzstadium column
demenzstadium_values = data['Demenzstadium (!)'].unique()
selected_demenzstadium = st.selectbox("Demenzstadium der betroffenen Person", demenzstadium_values)

# Filter rows based on the selected Demenzstadium value
filtered_data = data[data['Demenzstadium (!)'] == selected_demenzstadium]

# Select a value from the Hauptbereich column
hauptbereich_values = filtered_data['Hauptbereich'].unique()
selected_hauptbereich = st.selectbox("Dieses Thema beschäftig mich gerade", hauptbereich_values)

# Filter rows based on the selected Hauptbereich value
filtered_data = filtered_data[filtered_data['Hauptbereich'] == selected_hauptbereich]
selected_hauptbereich_str = filtered_data['Hauptbereich'].iloc[0]

# Check if there is more than one unique value in the Hauptbereich column
thema_values = filtered_data['Thema'].unique()
if len(thema_values) > 1:
    # Select a value from the Thema column
    selected_thema = st.selectbox(f"Über was in '{selected_hauptbereich_str}' möchtest du mehr erfahren", thema_values)

    # Filter rows based on the selected Thema value
    filtered_data = filtered_data[filtered_data['Thema'] == selected_thema]

##################
### COACH ########
##################

file_path = 'assets/text_resources/Wohnanpassung & Hilfsmittel.txt'
All_answers = process_file(file_path)

random_recomendation = choice(All_answers)

model_id = "sentence-transformers/all-MiniLM-L6-v2"
hf_token = st.secrets['api_key']
api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {hf_token}"}


output_dataset = query(All_answers, api_url, headers)
embeddings = pd.DataFrame(output_dataset)
dataset_embeddings = torch.from_numpy(embeddings.to_numpy()).to(torch.float)

#add spacing
st.write(f"####")
st.write(f"####")
st.write(f"### Verfeinere deine Suche mit Stichworten oder Stelle einer Frage zum Thema {filtered_data['Thema'].to_string(index=False)}")

# Create a form
with st.form("chat_form"):
    user_input = get_text()

    col1, col2, col3 = st.columns([0.25, 0.25, 0.5])

    with col1:
        submit_button = st.form_submit_button("Neue Antwort generieren")
    with col2:
        feedback_button = st.form_submit_button("Diese Antwort war hilfreich")


    # Check if the submit button is clicked
    if submit_button:
        if user_input:
            output_user = query([user_input], api_url, headers)
            query_embeddings = torch.FloatTensor(output_user)

            hits = semantic_search(query_embeddings, dataset_embeddings, top_k=1)

            answer = All_answers[hits[0][0]['corpus_id']]
            st.session_state.past.append(user_input)
            #temp fix: warning for not available content
            if filtered_data['Thema'].to_string(index=False) != "Wohnanpassung & Hilfsmittel":
                st.session_state.generated.append(f"Ich finde leider ich keine passende Antwort zu diesem Thema. Aber vielleicht hilft dir diese Anregung weiter: \n \n {random_recomendation}")
            else:
                st.session_state.generated.append(answer)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1,-1,-1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')


# reset chat button
if st.button('Reset Chat'):
    # Reset chat protocol
    st.session_state['generated'] = []
    st.session_state['past'] = []