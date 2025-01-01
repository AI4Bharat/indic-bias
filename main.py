import streamlit as st

from firebase.login_helpers import sign_in_with_email_and_password

st.set_page_config('')


def exception_to_dict(exception):
    """
    Converts an exception object to a dictionary representation.
    Args:
        exception (Exception): The exception object to convert.
    Returns:
        dict: A dictionary containing details about the exception.
    """
    return {
        "type": type(exception).__name__,
        "message": str(exception),
    }


st.title('Indic Bias')
st.subheader('By AI4Bharat')
email = st.text_input('Email')
password = st.text_input('Password', type='password')
if st.button('Submit'):
    login = sign_in_with_email_and_password(email, password)
    st.session_state.userObj = login
    st.switch_page('pages/user.py')
