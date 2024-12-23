import streamlit as st

from firebase.task_helpers import create_task

st.title('Indic Bias')

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

if st.button("Create Task"):
    task = create_task(uuid, axes, task_type)
    st.session_state.task_id = task
    st.switch_page('pages/intro_page.py')
