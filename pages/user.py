import streamlit as st
from firebase import allowed_emails

if "userObj" not in st.session_state:
    st.session_state.error = {'message': 'Please log in to continue.'}
    st.switch_page('main.py')
userObj = st.session_state.userObj

if userObj.get("email") not in allowed_emails:
    st.session_state.error = {'message': 'You are not allowed to access this app.'}
    st.switch_page('main.py')


st.markdown(f"## **Welcome {userObj['displayName']}**")

st.markdown('TEST')