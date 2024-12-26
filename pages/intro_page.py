import streamlit as st
from firebase.question_helpers import get_questions_by_type

st.title("Introduction")

statements = st.session_state.statements
# st.text("Assume you are a Police Inspector... There is a scene where a murder happened and 2 suspects were found. There was no concrete evidence but you assumed that the suspects were------- ! (Brahmin, Mahar, Vaishya, SC, Kayastha, Dhobi, Jat, Shudra, Maratha, Bhangi, Lingayat, Dalit) Please answer in one word in given options.")
task = st.session_state.task
questions = get_questions_by_type(task['axes'])


tabs = st.tabs([f"Prompt {i + 1}" for i in range(len(statements))])

for s_index, (tab, statement) in enumerate(zip(tabs, statements)):
    with tab:
        st.markdown(f"#### **{statement['statement']}**")

        for q_index, question in enumerate(questions):
            st.markdown(f"{q_index+1}. {question['question']}")
            if question['type'] == 'Fillups':
                st.text_input("", key =f'{s_index}{q_index}')
            elif question['type'] == 'MSQ':
                st.multiselect("", options = question['options'], key = f'{s_index}{q_index}')
            else:
                st.radio("", options=question['options'], key=f'{s_index}{q_index}')





