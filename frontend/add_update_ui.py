import streamlit as st
from datetime import datetime
import requests
import time
from encryption_helper import encrypt_expense, decrypt_expense

API_URL = "http://localhost:8000"


def get_headers():
    """Get headers with user authentication"""
    return {"user-id": str(st.session_state.user_id)}


def add_update_tab():
    # Check if encryption key exists
    if "encryption_key" not in st.session_state:
        st.error("🔒 Encryption key not found. Please log out and log in again.")
        return

    selected_date = st.date_input("Enter date", datetime(2024, 8, 1), label_visibility="collapsed")

    # Initialize session state
    if "num_expense_rows" not in st.session_state:
        st.session_state.num_expense_rows = 5
    if "rows_to_delete" not in st.session_state:
        st.session_state.rows_to_delete = set()
    if "show_submit_confirm" not in st.session_state:
        st.session_state.show_submit_confirm = False

    # Fetch and decrypt existing expenses
    response = requests.get(f"{API_URL}/expenses/{selected_date}", headers=get_headers())
    if response.status_code == 200:
        encrypted_expenses = response.json()
        # Decrypt expenses
        existing_expenses = [decrypt_expense(exp, st.session_state.encryption_key) for exp in encrypted_expenses]
        st.write(f"🔓 Loaded {len(existing_expenses)} expenses for {selected_date}")
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    categories = ["Rent", "Food", "Shopping", "Entertainment", "Other"]

    with st.form(key="expenses-form"):
        col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
        with col1:
            st.subheader("Amount")
        with col2:
            st.subheader("Category")
        with col3:
            st.subheader("Notes")
        with col4:
            st.subheader("Delete")

        expenses = []
        active_row_count = 0

        for i in range(st.session_state.num_expense_rows):
            if i in st.session_state.rows_to_delete:
                continue

            active_row_count += 1

            if i < len(existing_expenses):
                amount = existing_expenses[i]["amount"]
                category = existing_expenses[i]["category"]
                notes = existing_expenses[i]["notes"]
            else:
                amount = 0.0
                category = "Shopping"
                notes = ""

            col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
            with col1:
                amount_input = st.number_input("Amount", min_value=0.0, step=1.0, value=amount,
                                               key=f"amount_{i}_{selected_date}", label_visibility="collapsed")
            with col2:
                category_input = st.selectbox("Category", options=categories,
                                              index=categories.index(category) if category in categories else 0,
                                              key=f"category_{i}_{selected_date}", label_visibility="collapsed")
            with col3:
                notes_input = st.text_input("Notes", value=notes, key=f"notes_{i}_{selected_date}",
                                            label_visibility="collapsed")
            with col4:
                delete_row = st.form_submit_button("🗑️", key=f"delete_row_{i}", use_container_width=True)
                if delete_row:
                    st.session_state.rows_to_delete.add(i)
                    st.rerun()

            expenses.append({
                "amount": amount_input,
                "category": category_input,
                "notes": notes_input,
            })

        st.write(f"Active rows: {active_row_count}")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            add_more_button = st.form_submit_button(label="➕ Add More", use_container_width=True)
        with col2:
            clear_deleted_button = st.form_submit_button(label="🔄 Reset", use_container_width=True)
        with col3:
            submit_button = st.form_submit_button(label="✅ Submit", type="primary", use_container_width=True)

        if add_more_button:
            st.session_state.num_expense_rows += 3
            st.rerun()

        if clear_deleted_button:
            st.session_state.rows_to_delete = set()
            st.rerun()

        if submit_button:
            st.session_state.show_submit_confirm = True
            st.session_state.temp_expenses = expenses
            st.rerun()

    # Confirmation dialog
    if st.session_state.show_submit_confirm:
        st.warning("⚠️ Are you sure you want to submit these expenses?")
        st.write(f"This will update expenses for **{selected_date}**")

        filtered_expenses = [expense for expense in st.session_state.temp_expenses if expense["amount"] > 0]
        st.write(f"**Total expenses to submit:** {len(filtered_expenses)}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Submit", type="primary", use_container_width=True):
                # Encrypt expenses before sending
                encrypted_expenses = [encrypt_expense(exp, st.session_state.encryption_key) for exp in
                                      filtered_expenses]

                response = requests.post(f"{API_URL}/expenses/{selected_date}", json=encrypted_expenses,
                                         headers=get_headers())
                if response.status_code == 200:
                    st.success("✅ Successfully submitted expenses! (Encrypted)")
                    time.sleep(1.5)
                    st.session_state.num_expense_rows = 5
                    st.session_state.rows_to_delete = set()
                    st.session_state.show_submit_confirm = False
                    st.session_state.temp_expenses = []
                    st.rerun()
                else:
                    st.error("❌ Failed to submit expenses")
                    st.session_state.show_submit_confirm = False
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_submit_confirm = False
                st.rerun()