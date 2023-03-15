import streamlit as st
from streamlit_chat import message
import requests

##################
####### Chat Demo
##################

# Title
st.title("Interactive Coach")

# Chatbot API
API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
headers = {"Authorization": "Bearer {}".format(st.secrets['api_key'])}

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def get_text():
    input_text = st.text_input("**Was belastet dich gerade?** ","The patient doesn't want to eat", key="input")
    return input_text

user_input = get_text()

# reset chat button
if st.button('Reset Chat'):
    # Reset chat protocol
    st.session_state['generated'] = []
    st.session_state['past'] = []

if user_input:
    output = query({
        "inputs": {
            "past_user_inputs": st.session_state.past,
            "generated_responses": st.session_state.generated,
            "text": user_input,
        },"parameters": {"repetition_penalty": 1.33},
    })
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output["generated_text"])
#st.session_state['generated']
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])):

        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))

