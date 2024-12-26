import streamlit as st
from firebase_admin import credentials, initialize_app, get_app, firestore
from httpx_oauth.clients.google import GoogleOAuth2

app = None
try:
    app = get_app()
except ValueError:
    creds = credentials.Certificate(dict(st.secrets.get('serviceAccount')))
    app = initialize_app(creds)

db = firestore.client(app)

web_api_key = st.secrets.firebaseAPIKEY.key

oauth_client = GoogleOAuth2(client_id=st.secrets.oAuth.client_id, client_secret=st.secrets.oAuth.client_secret)
master_ref = db.collection('master')

emails_ref = db.collection('emails')
statements_ref = db.collection('statements')

allowed_emails = [doc.id for doc in emails_ref.stream()]
# DB INIT SCRIPT
'''

admin_emails = ['janani23ai@gmail.com', 'jsvigneshbabu83@gmail.com']
user_emails = ['21f3002138@ds.study.iitm.ac.in', '22f1001225@ds.study.iitm.ac.in']

for email in user_emails:
    emails_ref.document(email).set({'role': 'user'})

for email in admin_emails:
    emails_ref.document(email).set({'role': 'admin'})

'''
