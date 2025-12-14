import streamlit as st
import requests
import time
from encryption_helper import get_encryption_key

API_URL = "http://localhost:8000"


def login_page():
    st.title("🔐 Expense Tracker Login")

    # Show encryption notice
    st.info("🔒 Your data is encrypted end-to-end. Only you can decrypt it with your password.")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                try:
                    response = requests.post(f"{API_URL}/login", json={
                        "username": username,
                        "password": password
                    })

                    if response.status_code == 200:
                        data = response.json()

                        # Generate and store encryption key
                        encryption_key = get_encryption_key(password, username)

                        st.session_state.user_id = data["user_id"]
                        st.session_state.username = data["username"]
                        st.session_state.encryption_key = encryption_key
                        st.session_state.authenticated = True

                        st.success(f"✅ Welcome back, {data['username']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please enter both username and password")

    with tab2:
        st.subheader("Create New Account")

        st.warning(
            "⚠️ IMPORTANT: Your password is your ONLY decryption key. If you forget it, your data CANNOT be recovered!")

        new_username = st.text_input("Choose Username", key="register_username")
        new_password = st.text_input("Choose Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Register", type="primary", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters long for security")
                else:
                    try:
                        response = requests.post(f"{API_URL}/register", json={
                            "username": new_username,
                            "password": new_password
                        })

                        if response.status_code == 200:
                            st.success("✅ Account created successfully! Please switch to the Login tab to sign in.")
                            st.info("🔑 Remember your password! It's your encryption key and cannot be recovered.")
                        else:
                            error_detail = response.json().get("detail", "Failed to create account")
                            st.error(f"❌ {error_detail}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please fill in all fields")


def logout():
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.encryption_key = None  # Clear encryption key

    # Clear expenses data on logout
    if "expenses_data" in st.session_state:
        del st.session_state.expenses_data

    st.rerun()