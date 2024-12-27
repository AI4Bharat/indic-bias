import streamlit as st

from firebase.question_helpers import get_questions_by_type

st.set_page_config(layout="wide")

st.title("Introduction")

if 's_index' not in st.session_state:
    st.session_state['s_index'] = 0


def next_element():
    st.session_state['s_index'] += 1


def previous_element():
    st.session_state['s_index'] -= 1


statements = st.session_state.statements

curr_statement = statements[st.session_state.s_index]

task = st.session_state.task
questions = get_questions_by_type(task['axes'])

if "answers" not in st.session_state:
    st.session_state['answers'] = {}

    for s_index in range(len(statements)):
        st.session_state['answers'][s_index] = {}

l, c, r = st.columns(3)

with l:
    st.button('Previous', on_click=previous_element, disabled=st.session_state['s_index'] == 0)
with c:
    st.write(f"Statement {st.session_state.s_index + 1}/{len(statements)}")
with r:
    st.button('Next', on_click=next_element, disabled=st.session_state['s_index'] == len(statements) - 1)

st.markdown(f"#### **{curr_statement['statement']}**")

answers = st.session_state.answers[st.session_state.s_index]

for q_index, question in enumerate(questions):
    st.markdown(f"{q_index + 1}. {question['question']}")
    if question['type'] == 'Fillups':
        answers[q_index] = st.text_input("", value=answers.get(q_index), key=f'{st.session_state.s_index}{q_index}')
    elif question['type'] == 'MSQ':
        answers[q_index] = st.multiselect("", default=answers.get(q_index), options=question['options'], key=f'{st.session_state.s_index}{q_index}')
    else:
        answers[q_index] = st.radio("", index=question['options'].index(answers.get(q_index)) if answers.get(q_index) else 0,
                                    options=question['options'],
                                    key=f'{st.session_state.s_index}{q_index}')

l_down, c_down, r_down = st.columns(3)

with l_down:
    st.button('Previous', on_click=previous_element, disabled=st.session_state['s_index'] == 0, key='down_0')
with c_down:
    st.write(f"Statement {st.session_state.s_index + 1}/{len(statements)}", key='down_1')
with r_down:
    st.button('Next', on_click=next_element, disabled=st.session_state['s_index'] == len(statements) - 1, key='down_2')

