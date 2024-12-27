import streamlit as st

from firebase import allowed_emails
from firebase.question_helpers import get_statements_by_type

if "userObj" not in st.session_state:
    st.session_state.error = {'message': 'Please log in to continue.'}
    st.switch_page('main.py')

userObj = st.session_state.userObj

if userObj.get("email") not in allowed_emails:
    st.session_state.error = {'message': 'You are not allowed to access this app.'}
    st.switch_page('main.py')

st.markdown(f"## **Welcome {userObj['displayName']}**")
if "userObj" in st.session_state:
    userObj = st.session_state["userObj"]
    uuid = userObj.get('localId')

else:
    st.session_state.error = {'message': 'Please login first'}
    st.switch_page('main.py')

axes_types = ["Bias", "Stereotype", "Toxicity", "Harmful Activities"]
task_types = ['Sentiment', 'Plausibility', 'Judgement', 'Classification', 'Generation']

axes = st.selectbox("Axes", axes_types)
task_type = st.selectbox("Task Types", task_types)

if st.button("Next"):
    task = {"axes":axes,"type":task_type}

    st.session_state.task = task
    st.session_state.statements = get_statements_by_type(axes, task_type)
    st.switch_page('pages/intro_page.py')
