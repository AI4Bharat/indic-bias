import streamlit as st

from firebase.question_helpers import get_statements_by_type,get_all_types



if "statements" in st.session_state:
    del st.session_state["statements"]

if "userObj" not in st.session_state:
    st.session_state.error = {'message': 'Please log in to continue.'}
    st.switch_page('main.py')

userObj = st.session_state.userObj

st.markdown(f"## **Welcome {userObj['displayName']}**")
if "userObj" in st.session_state:
    userObj = st.session_state["userObj"]
    uuid = userObj.get('localId')

else:
    st.session_state.error = {'message': 'Please login first'}
    st.switch_page('main.py')

#
# st.write(uuid)

if "message" in st.session_state:
    st.toast(st.session_state.message['message'])
    del st.session_state["message"]

axes_types = get_all_types(uuid)

axes = axes_types['axes']
types = axes_types['types']

axes = st.selectbox("Axes", axes,format_func=lambda x:x[0].upper()+x[1:])
task_type = st.selectbox("Task Types", types,format_func=lambda x:x[0].upper()+x[1:])

if st.button("Next"):
    task = {"axes": axes, "type": task_type}
    if "answers" in st.session_state:
        del st.session_state["answers"]
    if "s_index" in st.session_state:
        del st.session_state["s_index"]
    st.session_state.task = task
    st.session_state.statements = get_statements_by_type(axes=axes.lower(), statement_type=task_type.lower(),uuid=uuid)
    st.switch_page('pages/intro_page.py')
