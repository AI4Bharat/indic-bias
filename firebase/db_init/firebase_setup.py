import json
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Define the path to secrets.json
secrets_path = os.path.join(os.path.dirname(__file__), "../.streamlit/secrets.json")

# Load the JSON data
with open(secrets_path, "r") as file:
    creds = json.load(file)

# Initialize Firebase
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(creds)
    app = firebase_admin.initialize_app(cred)

db = firestore.client(database_id="indic-bias")

# Creating Email Collection
for i in range(1, 13):
    db.collection('emails').document(f"user{i}@gmail.com").set({"role": "user"})

# Creating Master Collection (User Authentication)
users = [{"display_name": f"User {i}", "email": f"user{i}@gmail.com", "password": f"user_{i}"} for i in range(1, 13)]
for user in users:
    try:
        user_ref = auth.get_user_by_email(user['email'])
    except:
        user_ref = auth.create_user(**user)
    user.pop('password')
    db.collection("master").document(user_ref.uid).set(user)
