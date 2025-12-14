import streamlit as st


def apply_responsive_styles():
    st.markdown("""
        <style>
        /* Base responsive settings */
        @media (max-width: 768px) {
            /* Mobile styles */
            .stButton button {
                width: 100%;
                margin-bottom: 10px;
            }

            .stNumberInput, .stSelectbox, .stTextInput {
                width: 100% !important;
            }

            /* Make columns stack on mobile */
            .row-widget.stHorizontal {
                flex-direction: column !important;
            }

            /* Adjust form spacing */
            .stForm {
                padding: 10px;
            }

            /* Adjust expander width */
            .streamlit-expanderHeader {
                font-size: 14px;
            }

            /* Table responsiveness */
            .stTable {
                overflow-x: auto;
            }
        }

        @media (min-width: 769px) {
            /* Desktop styles */
            .stButton button {
                padding: 10px 24px;
            }
        }

        /* Make primary buttons green and responsive */
        button[kind="primary"] {
            background-color: #00cc66 !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
        }

        button[kind="primary"]:hover {
            background-color: #00aa55 !important;
        }

        /* Responsive containers */
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }

        /* Better mobile navigation */
        @media (max-width: 768px) {
            .stTabs [data-baseweb="tab-list"] {
                gap: 2px;
            }

            .stTabs [data-baseweb="tab"] {
                padding: 8px 12px;
                font-size: 14px;
            }
        }
        </style>
    """, unsafe_allow_html=True)