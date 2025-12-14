import streamlit as st
import requests

API_URL = "http://localhost:8000"


def login_page():
    st.title("🔐 Expense Tracker Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                response = requests.post(f"{API_URL}/login", json={
                    "username": username,
                    "password": password
                })

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.user_id = data["user_id"]
                    st.session_state.username = data["username"]
                    st.session_state.authenticated = True
                    st.success(f"Welcome back, {data['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")

    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Choose Username", key="register_username")
        new_password = st.text_input("Choose Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Register", type="primary", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    response = requests.post(f"{API_URL}/register", json={
                        "username": new_username,
                        "password": new_password
                    })

                    if response.status_code == 200:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error(response.json().get("detail", "Failed to create account"))
            else:
                st.warning("Please fill in all fields")


def logout():
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()