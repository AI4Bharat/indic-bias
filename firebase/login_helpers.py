import asyncio
import json

import requests
import streamlit as st

from firebase import web_api_key, oauth_client, master_ref, firestore


def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise requests.exceptions.HTTPError(error, request_object.text)


def sign_in_with_email_and_password(email, password):
    request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(web_api_key)
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    request_object = requests.post(request_ref, headers=headers, data=data)
    raise_detailed_error(request_object)
    return request_object.json()


def sign_in_with_oauth(code, request_uri=st.secrets.oAuth.redirect_uri, provider_id="google.com"):
    access_token = asyncio.run(get_token(code))

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={web_api_key}"
    headers = {"Content-Type": "application/json"}

    post_body = f"id_token={access_token.get('id_token')}&providerId={provider_id}"
    payload = {
        "postBody": post_body,
        "requestUri": request_uri,
        "returnIdpCredential": True,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print("HTTP error occurred:", err)
        return None
    except Exception as err:
        print("An error occurred:", err)
        return None


def getAuthorisationLink():
    authorization_url = asyncio.run(oauth_client.get_authorization_url(
        st.secrets.oAuth.redirect_uri,
        scope=["email", "profile"],
    ))
    return authorization_url


def create_user_doc(userObj):
    uuid = userObj.get('localId')
    user_ref = master_ref.document(uuid)

    user_details = {
        'email': userObj['email'],
        'name': userObj['displayName'],
        'createdAt': firestore.SERVER_TIMESTAMP
    }
    if not user_ref.get().to_dict():
        user_ref.set(user_details)

    return True


async def get_token(code):
    result = await oauth_client.get_access_token(code, st.secrets.oAuth.redirect_uri)
    return result
