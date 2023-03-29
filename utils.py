import requests
import streamlit as st
# Load file and precompute answers
@st.cache_data
def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    lines = content.split('\n')
    paragraphs = [line.strip().replace('\xad', '') for line in lines if line.strip()]
    return paragraphs

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
