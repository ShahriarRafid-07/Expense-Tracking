import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import os
API_URL = os.getenv("API_URL", "http://localhost:8000")

def get_headers():
    """Get headers with user authentication"""
    return {"user-id": str(st.session_state.user_id)}

def view_manage_tab():
    st.title("View & Manage Expenses")

    # Initialize session state for delete confirmation
    if "delete_confirm" not in st.session_state:
        st.session_state.delete_confirm = None

    # Fetch all expenses
    if st.button("Refresh Data") or "expenses_data" not in st.session_state:
        response = requests.get(f"{API_URL}/expenses/", headers=get_headers())
        if response.status_code == 200:
            st.session_state.expenses_data = response.json()
            st.success("Data refreshed!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Failed to load expenses")
            return

    if "expenses_data" in st.session_state and len(st.session_state.expenses_data) > 0:
        expenses = st.session_state.expenses_data

        # Convert to DataFrame for better display
        df = pd.DataFrame(expenses)
        df['expense_date'] = pd.to_datetime(df['expense_date'])
        df['year_month'] = df['expense_date'].dt.to_period('M')

        st.subheader(f"Total Expenses: {len(df)}")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            categories = ["All"] + list(df['category'].unique())
            selected_category = st.selectbox("Filter by Category", categories)

        with col2:
            # Get unique year-month combinations
            available_months = sorted(df['year_month'].unique(), reverse=True)
            month_options = ["All"] + [str(month) for month in available_months]
            selected_month = st.selectbox("Filter by Month", month_options)

        # Apply filters
        filtered_df = df.copy()
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        if selected_month != "All":
            filtered_df = filtered_df[filtered_df['year_month'] == pd.Period(selected_month)]

        # Sort by date descending
        filtered_df = filtered_df.sort_values('expense_date', ascending=False)

        st.write(f"Showing {len(filtered_df)} expenses")

        # Group by date and display
        filtered_df['date_str'] = filtered_df['expense_date'].dt.strftime('%Y-%m-%d')
        grouped = filtered_df.groupby('date_str')

        for date, group in grouped:
            daily_total = group['amount'].sum()
            with st.expander(f"📅 {date} | {len(group)} expenses | Total: ${daily_total:.2f}", expanded=False):

                for idx, row in group.iterrows():
                    st.divider()
                    col1, col2, col3 = st.columns([3, 3, 1])

                    with col1:
                        st.write(f"**Category:** {row['category']}")
                        st.write(f"**Amount:** ${row['amount']:.2f}")
                        st.write(f"**Notes:** {row['notes']}")
                        st.write(f"**ID:** {row['id']}")

                    with col2:
                        # Edit form
                        with st.form(key=f"edit_form_{row['id']}"):
                            st.write("**Edit Expense**")
                            new_amount = st.number_input("Amount", value=float(row['amount']), min_value=0.0, step=1.0, key=f"amount_{row['id']}")
                            categories_list = ["Rent", "Food", "Shopping", "Entertainment", "Other"]
                            new_category = st.selectbox("Category", categories_list, index=categories_list.index(row['category']) if row['category'] in categories_list else 0, key=f"cat_{row['id']}")
                            new_notes = st.text_input("Notes", value=row['notes'], key=f"notes_{row['id']}")

                            if st.form_submit_button("Update", use_container_width=True):
                                update_data = {
                                    "amount": new_amount,
                                    "category": new_category,
                                    "notes": new_notes
                                }
                                response = requests.put(f"{API_URL}/expenses/{row['id']}", json=update_data, headers=get_headers())
                                if response.status_code == 200:
                                    st.success("✅ Expense updated successfully!")
                                    time.sleep(1.5)
                                    # Refresh data
                                    response = requests.get(f"{API_URL}/expenses/", headers=get_headers())
                                    if response.status_code == 200:
                                        st.session_state.expenses_data = response.json()
                                    st.rerun()
                                else:
                                    st.error("Failed to update expense")

                    with col3:
                        st.write("")
                        st.write("")
                        # Delete button with confirmation
                        if st.button("🗑️ Delete", key=f"delete_btn_{row['id']}"):
                            st.session_state.delete_confirm = row['id']

                        # Show confirmation dialog
                        if st.session_state.delete_confirm == row['id']:
                            st.warning("⚠️ Are you sure?")
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ Yes", key=f"confirm_yes_{row['id']}"):
                                    response = requests.delete(f"{API_URL}/expenses/{row['id']}", headers=get_headers())
                                    if response.status_code == 200:
                                        st.success("🗑️ Expense deleted!")
                                        time.sleep(1.5)
                                        # Refresh data
                                        response = requests.get(f"{API_URL}/expenses/", headers=get_headers())
                                        if response.status_code == 200:
                                            st.session_state.expenses_data = response.json()
                                        st.session_state.delete_confirm = None
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete expense")
                            with col_no:
                                if st.button("❌ No", key=f"confirm_no_{row['id']}"):
                                    st.session_state.delete_confirm = None
                                    st.rerun()
    else:
        st.info("No expenses found. Add some expenses first!")
