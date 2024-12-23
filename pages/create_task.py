import streamlit as st
st.title('Indic Bias')
axes = ["Bias", "Stereotype", "Toxicity", "Harmful Activities"]
task_types = ["A", "B", "C", "D", "E"]
st.selectbox("Axes", axes)
st.selectbox("Task Types", task_types)
if st.button("Create Task"):
    st.switch_page('pages/intro_page.py')


