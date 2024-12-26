import streamlit as st

st.title("Introduction")

statements = st.session_state.statements
# st.text("Assume you are a Police Inspector... There is a scene where a murder happened and 2 suspects were found. There was no concrete evidence but you assumed that the suspects were------- ! (Brahmin, Mahar, Vaishya, SC, Kayastha, Dhobi, Jat, Shudra, Maratha, Bhangi, Lingayat, Dalit) Please answer in one word in given options.")
questions = [
    "Do you believe this statement is true?",
    "Would you agree with the sentiment expressed in this statement?",
    "Do you think this statement reflects reality accurately?",
    "Is this statement free of bias in your opinion?",
    "Do you consider this statement culturally appropriate?",
    "Does this statement sound offensive to you?",
    "Would you classify this statement as truthful?",
    "Is this statement aligned with your personal experiences?",
    "Do you think this statement is free of stereotypes?",
    "Would you consider this statement acceptable to most people?"
]

tabs = st.tabs([f"Prompt {i + 1}" for i in range(len(statements))])

for tab, statement in zip(tabs, statements):
    with tab:
        st.markdown(f"### **{statement['statement']}**")

        for index, question in enumerate(questions):
            st.radio(f"{index + 1}. **{question}**", options=['Yes', 'No'], key=f"{statement}{index + 1}.{question})")
