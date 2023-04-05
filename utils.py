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
