import streamlit as st
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab
from monthly_analytics_ui import monthly_analytics_tab
from view_manage_ui import view_manage_tab
from auth_ui import login_page, logout
import os
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Set page config
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# Check authentication
if not st.session_state.authenticated:
    login_page()
else:
    # Show logout button and username
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("Expense Tracking System")
    with col2:
        st.write(f"👤 {st.session_state.username}")
        if st.button("Logout", use_container_width=True):
            logout()

    tab1, tab2, tab3, tab4 = st.tabs(["Add/Update", "Analytics", "Monthly Analytics", "View & Manage"])

    with tab1:
        add_update_tab()

    with tab2:
        analytics_tab()

    with tab3:
        monthly_analytics_tab()

    with tab4:
        view_manage_tab()
