import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth

with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config["credentials"],
    cookie_key="some_signature_key",
    cookie_name="some_cookie_name",
    cookie_expiry_days=30,
)

st.title("Sign in Admin")

def auth():
    authenticator.login()
    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
        st.write('Some content')
    elif st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your username and password")