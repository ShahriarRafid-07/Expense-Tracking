import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL = "http://localhost:8000"


def get_headers():
    """Get headers with user authentication"""
    if "user_id" not in st.session_state or st.session_state.user_id is None:
        st.error("User not authenticated. Please log in again.")
        return None
    return {"user-id": str(st.session_state.user_id)}


def monthly_analytics_tab():
    st.title("Monthly Expense Analytics")

    current_year = datetime.now().year
    years = list(range(2020, current_year + 1))
    selected_year = st.selectbox("Select Year", years, index=len(years) - 1)

    if st.button("Get Monthly Analytics"):
        headers = get_headers()
        if headers is None:
            return

        try:
            response = requests.post(f"{API_URL}/analytics_month/", params={"year": selected_year}, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if len(data) == 0:
                    st.warning(f"No expense data found for {selected_year}. Add some expenses first!")
                else:
                    df = pd.DataFrame(data)

                    st.subheader(f"Monthly Expenses for {selected_year}")
                    st.bar_chart(data=df.set_index("month_name")["total"], use_container_width=True)

                    st.subheader("Monthly Breakdown")
                    display_df = df[["month_name", "total"]].copy()
                    display_df.columns = ["Month", "Total (USD)"]
                    display_df["Total (USD)"] = display_df["Total (USD)"].map("${:,.2f}".format)

                    st.table(display_df)

                    total_year = df["total"].sum()
                    st.metric("Total Expenses for year", f"${total_year:,.2f}")
            elif response.status_code == 401:
                st.error("❌ Authentication failed. Please log out and log in again.")
            else:
                st.error(f"Failed to retrieve monthly analytics.")
        except Exception as e:
            st.error(f"Error connecting to server: {str(e)}")