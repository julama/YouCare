import streamlit as st
from coach_tools import display_book, parse_text_file

# Load existing text resources
if "text_resources" not in st.session_state:
    st.session_state["text_resources"] = parse_text_file("assets/text_resources/Körperpflege.txt")
Pflege_dicts = st.session_state["text_resources"]

st.title("Mein Körperpflege Coach")

# Segment 1: Display summaries and navigation buttons
summary_topic = "Zusammenfassung"
topics = list(Pflege_dicts.keys())
topic_summaries = {topic: Pflege_dicts[topic][summary_topic] for topic in topics}
summary_sections = list(topic_summaries.keys())
current_summary_index = st.session_state.get("current_summary_index", 0)

if "selected_challenges" not in st.session_state:
    st.session_state.selected_challenges = set()


st.write(" ")
st.write(" ")

st.subheader(f"{summary_sections[current_summary_index]}")
content = topic_summaries[summary_sections[current_summary_index]]

if isinstance(content, dict):
    content = " ".join([value for value in content.values()])

button_columns = st.columns(3)

if "current_summary_index" not in st.session_state:
    st.session_state.current_summary_index = 0
def forward():
    #st.session_state['_'+key] = st.session_state[key]
    st.session_state.current_summary_index += 1
def back():
    #st.session_state['_'+key] = st.session_state[key]
    st.session_state.current_summary_index -= 1

# Previous button logic
if current_summary_index > 0:
    button_columns[0].button("zurück", on_click=back)

# Next button logic
if current_summary_index < len(summary_sections) - 1:
    button_columns[2].button("weiter", on_click=forward)

# Bookmark button logic
bookmark_icon = "💾"
selected_sections = st.session_state.get("selected_sections", set())
if button_columns[1].button(bookmark_icon):
    selected_sections.add(summary_sections[current_summary_index])
    st.session_state.selected_sections = selected_sections
st.write(content)
st.write(" ")
st.write(" ")

# Segment 3: Display challenges and solutions
st.subheader("Herausforderungen")

# Get the challenges_topic from the first key in Pflege_dicts
first_key = list(Pflege_dicts.keys())[0]
challenges_topic = Pflege_dicts[first_key]

# Get the challenges for the selected topic
challenges = challenges_topic["Herausforderungen"]

# Display challenge boxes that can be selected
selected_challenges = st.session_state.selected_challenges

for challenge_title, challenge_content in challenges.items():
    button_key = f"{challenge_title}_button"
    button_text = "Challenge Title"
    st.write(challenge_content)


st.write(" ")
st.write(" ")

# Segment 2: Display section names as checkboxes
st.subheader("Meine Themen")

checkbox_columns = st.columns(3)
num_sections = len(summary_sections)
num_sections_per_column = num_sections // 3
remainder = num_sections % 3

current_section_index = 0
for col in range(3):
    num_sections_in_col = num_sections_per_column + (1 if col < remainder else 0)
    for _ in range(num_sections_in_col):
        section_name = summary_sections[current_section_index]
        is_checked = section_name in selected_sections
        if checkbox_columns[col].checkbox(section_name, value=is_checked):
            selected_sections.add(section_name)
        else:
            selected_sections.discard(section_name)
        st.session_state.selected_sections = selected_sections
        current_section_index += 1


st.write(" ")
st.write(" ")

# Segment 3: Display challenges and solutions
st.subheader("Lösungen und Tipps")
