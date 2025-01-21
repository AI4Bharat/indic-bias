import streamlit as st

from firebase.question_helpers import get_questions_by_type, get_statement_by_user
from firebase.question_helpers import store_answers

flag = False
st.set_page_config(layout="wide")
st.title("Introduction")

if 's_index' not in st.session_state:
    st.session_state['s_index'] = 0


# THWWaKrElqXm8UyDhcdH

def previous_element():
    st.session_state['s_index'] -= 1


def trigger_change(target, value):
    target = value


task = st.session_state.task
uuid = st.session_state.userObj.get('localId')

statements = get_statement_by_user(uuid, task['axes'], task['type'])
statement_ids = list(map(lambda x: x['id'], statements))

try:
    curr_statement = statements[st.session_state.s_index]
except IndexError:
    st.session_state.message = {"message": "This task is either completed or it has not been assigned yet"}
    st.switch_page("pages/user.py")

questions = get_questions_by_type(task['axes'], task['type'])


l, c, r = st.columns(3)

with c:
    st.write(f"Statement {st.session_state.s_index + 1}/{len(statements)}")

with st.container():
    statement = curr_statement['statement']
    
    # st.write(curr_statement)


    if curr_statement['axes'] == "bias":


        row1 = st.columns(2)
        with row1[0]:
            with st.container(border=True):
                st.subheader("Positive Template")
                st.write(statement['positive_template'].replace('<', '&lt;').replace('>', '&gt;'))

                st.subheader("Negative Template")
                st.write(statement['negative_template'].replace('<', '&lt;').replace('>', '&gt;'))
        with row1[1]:
            with st.container(border=True):
                st.subheader("Topic")
                st.write(statement['topic'])

                st.subheader("Description")
                st.write(statement['topic_description'])

            with st.container(border=True):
                st.subheader("Concept")
                st.write(statement['concept'])

                st.subheader("Description")
                st.write(statement['concept_description'])



    if curr_statement['axes'] == "stereotype"  and curr_statement["type"] == "generation":


        row1 = st.columns(2)
        with row1[0]:
            with st.container(border=True):
                st.subheader("Scenario")
                st.write(statement['scenario'])

                st.subheader("True Pairs")

                st.table([statement['true_pairs']])
        with row1[1]:
            with st.container(border=True):
                st.subheader("Identity 1")
                st.write(statement['identity_1'])

                st.subheader("Identity 2")
                st.write(statement['identity_2'])

            with st.container(border=True):
                st.subheader("Stereotype 1")
                st.write(statement['stereotype_1'])

                st.subheader("Stereotype 1")
                st.write(statement['stereotype_2'])

    if curr_statement['axes'] == "stereotype"  and curr_statement["type"] in ["judgement", "plausible"]:
        row1 = st.columns(2)
        with row1[0]:
            with st.container(border=True):
                st.subheader("Template")
                st.write(statement['template'])

                st.subheader("Category")
                st.write(statement['category'])
        with row1[1]:
            with st.container(border=True):
                st.subheader("Identity")
                st.write(statement['identity'])

                st.subheader("Identity Type")
                st.write(statement['identity_type'])

            with st.container(border=True):
                st.subheader("Stereotype")
                st.write(statement['stereotype'])

                # st.subheader("Stereotype 1")
                # st.write(statement['stereotype_2'])

answer = st.radio(curr_statement['questions']['question'], options=curr_statement['questions']['options'])

def next_element():
    store_answers(uuid, answer, curr_statement['id'])
    if st.session_state['s_index'] < len(statements):
        st.session_state['s_index'] += 1
    else:
        st.session_state.message = {"message": "You have completed this successfully !!!"}
        st.switch_page("pages/user.py")

if st.button("Submit", on_click=next_element):
    st.toast('Saved Successfully')
    if st.session_state['s_index'] == len(statements) - 1:
        st.switch_page("pages/user.py")

