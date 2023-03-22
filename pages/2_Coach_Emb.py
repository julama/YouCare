import streamlit as st
from streamlit_chat import message
import requests
import pandas as pd
import torch
from sentence_transformers.util import semantic_search
from random import choice
st.session_state['generated'] = []
st.session_state['past'] = []

st.title("Interaktiver Coach")

# Load the pre-defined CSV file
file_path = "assets/Kategorien_Sortierkriterien.csv"
data = pd.read_csv(file_path)

st.write("### Was belastet dich gerade?")

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

# Load file and precompute answers
def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    lines = content.split('\n')
    paragraphs = [line.strip().replace('\xad', '') for line in lines if line.strip()]
    return paragraphs

file_path = 'assets/text_resources/Wohnanpassung & Hilfsmittel.txt'
All_answers = process_file(file_path)

# Random tipps from topic
st.write(f"#### Anregungen zum Thema {filtered_data['Thema'].to_string(index=False)}:")
st.write(choice(All_answers))

model_id = "sentence-transformers/all-MiniLM-L6-v2"
hf_token = st.secrets['api_key']
api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {hf_token}"}

#@retry(tries=3, delay=10)
def query(texts):
    response = requests.post(api_url, headers=headers, json={"inputs": texts})
    result = response.json()
    if isinstance(result, list):
        return result
    elif list(result.keys())[0] == "error":
        st.info('Bitte habe einen Moment Geduld. Der Coach wird geladen')

output_dataset = query(All_answers)
embeddings = pd.DataFrame(output_dataset)
dataset_embeddings = torch.from_numpy(embeddings.to_numpy()).to(torch.float)

st.write(f"#### Stelle eine Frage zum Thema {filtered_data['Thema'].to_string(index=False)}")
def get_text():
    input_text = st.text_input(f"", "Schreibe hier deine Frage", key="input")
    return input_text

user_input = get_text()

# reset chat button
if st.button('Reset Chat'):
    # Reset chat protocol
    st.session_state['generated'] = []
    st.session_state['past'] = []

if user_input:
    output_user = query([user_input])
    query_embeddings = torch.FloatTensor(output_user)

    hits = semantic_search(query_embeddings, dataset_embeddings, top_k=1)

    answer = All_answers[hits[0][0]['corpus_id']]
    st.session_state.past.append(user_input)
    st.session_state.generated.append(answer)

if st.session_state['generated']:
    for i in range(0, len(st.session_state['generated'])):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))



