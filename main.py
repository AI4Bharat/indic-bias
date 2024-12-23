import streamlit as st

from firebase.login_helpers import sign_in_with_oauth, getAuthorisationLink
from firebase import allowed_emails

st.title('Indic Bias')
st.subheader('By AI4Bharat')

if st.query_params.get('code'):
    with st.spinner('Logging in'):
        oAuth_code = st.query_params.get('code')
        userObj = sign_in_with_oauth(oAuth_code)
    st.session_state.userObj = userObj

    st.switch_page('pages/user.py')

else:
    st.markdown(
        f"""
        <a href="{getAuthorisationLink()}" target="_self">
            <button style="background-color: #4285F4; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px;">
                Sign in with Google
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )
