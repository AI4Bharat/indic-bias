import streamlit as st
from firebase_admin import credentials,initialize_app,firestore,get_app

app = None
try:
    app = get_app()
except ValueError:
    creds = credentials.Certificate(dict(st.secrets.get('serviceAccount')))
    app = initialize_app(creds)

web_api_key = st.secrets.firebaseAPIKEY.key
