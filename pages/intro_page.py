import streamlit as st

from firebase.question_helpers import get_questions_by_type, get_statement_by_user
from firebase.question_helpers import store_answers
flag = False
st.set_page_config(layout="wide")
st.title("Introduction")

if 's_index' not in st.session_state:
    st.session_state['s_index'] = 0


def next_element():
    if st.session_state['s_index'] < len(statements) - 1:
        st.session_state['s_index'] += 1
    else:
        st.session_state.message = {"message": "You have completed this successfully !!!"}
        st.switch_page("pages/user.py")


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



    st.session_state.message  =  {"message": "This task is either completed or it has not been assigned yet"}
    st.switch_page("pages/user.py")
# st.markdown(f" <h3 style='text-align: center;'> {curr_statement['statement']}</h3>", unsafe_allow_html=True)


questions = get_questions_by_type(task['axes'], task['type'])

if "answers" not in st.session_state:
    st.session_state['answers'] = {}

    for statement in statements:
        st.session_state['answers'][statement['id']] = {}

        for q_index, question in enumerate(questions):
            question_copy = question.copy()
            if "options" in question_copy:
                del question_copy["options"]
            st.session_state['answers'][statement['id']][q_index] = {**question_copy}

l, c, r = st.columns(3)

# with l:
#     st.button('Previous', on_click=previous_element, disabled=st.session_state['s_index'] == 0)
with c:
    st.write(f"Statement {st.session_state.s_index + 1}/{len(statements)}")
# with r:
#     st.button('Next', on_click=next_element, disabled=st.session_state['s_index'] == len(statements) - 1)

with st.container(border=True):
    st.markdown(f" <h3 style='text-align: center;'> {curr_statement['statement']}</h3>", unsafe_allow_html=True)

answers = st.session_state.answers[statement_ids[st.session_state.s_index]]


def update_dict(answer_key, element_key):
    def callback():
        answers[answer_key]['answer'] = st.session_state[element_key]

    return callback


def all_questions_answered():
    current_answers = st.session_state.answers[statement_ids[st.session_state.s_index]]
    for q_index, question in enumerate(questions):
        # Check if the answer exists and is non-empty
        answer = current_answers[q_index].get('answer', None)
        if question['type'] == 'text' and not answer:  # For text questions
            return False
        elif question['type'] == 'msq' and not answer:  # For multiple select questions
            return False
        elif question['type'] != 'text' and question['type'] != 'msq' and answer is None:  # For radio buttons or other types
            return False
    return True


for q_index, question in enumerate(questions):
    st.markdown(f"<h5>{q_index + 1}. {question['question']}<h5>", unsafe_allow_html=True)

    if question['type'] == 'text':
        answers[q_index]['answer'] = st.text_input("Enter your answer",
                                                   value=answers[q_index].get('answer', ''),
                                                   key=f'{st.session_state.s_index}{q_index}',
                                                   on_change=update_dict(q_index, f'{st.session_state.s_index}{q_index}'),
                                                   label_visibility="collapsed",
                                                   )
    elif question['type'] == 'msq':
        answers[q_index]['answer'] = st.multiselect("Select your answer",
                                                    default=answers[q_index].get('answer', []),
                                                    options=question['options'],
                                                    key=f'{st.session_state.s_index}{q_index}',
                                                    label_visibility="collapsed")
    else:
        answers[q_index]['answer'] = st.radio("Select your answer",
                                              index=question['options'].index(answers[q_index].get('answer')) if answers[q_index].get('answer') in
                                                                                                                 question['options'] else 0,
                                              options=question['options'],
                                              key=f'{st.session_state.s_index}{q_index}',
                                              label_visibility="collapsed")
is_submit_enabled = all_questions_answered()
if st.button("Submit", disabled=not is_submit_enabled, on_click=next_element) :


    store_answers(uuid, st.session_state.answers, statement_ids[st.session_state.s_index])
    st.toast('Saved Successfully')
    if st.session_state['s_index']  ==  len(statements) - 1:
        st.switch_page("pages/user.py")




    # st.session_state['redirect'] = True
