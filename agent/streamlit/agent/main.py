import streamlit as st
from streamlit_navigation_bar import st_navbar
from pages.chatbot_page import render_chatbot_page
from pages.leave_request_page import render_leave_request_page
from pages.info_page import render_info_page
from pages.account_page import render_account_page

st.set_page_config(page_title="Chatbot Nhân sự NexusTech", layout="wide")

page = st_navbar(
    ["Chatbot", "Yêu cầu nghỉ phép", "Thông tin", "Tài khoản nhân viên"],
    styles={
        "nav": {"background-color": "#99ccff", "padding": "0.5rem"},
        "a": {
            "color": "white",
            "padding": "0.75rem",
            "text-decoration": "none",
            "border-radius": "5px",
            "font-size": "16px",
            "font-weight": "400",
            "display": "inline-block",
        },
        #"hover": {"background-color": "#3399FF", "color": "white"},
        "hover": {"color": "black"},
        #"active": {"background-color": "white", "color": "black", "border-radius": "6px", "text-decoration": "none"},
        "active": {"color": "black", "border-radius": "5px", "text-decoration": "none","font-size": "18px"},
    },
)

if page == "Chatbot":
    render_chatbot_page()
elif page == "Yêu cầu nghỉ phép":
    render_leave_request_page()
elif page == "Thông tin":
    render_info_page()
elif page == "Tài khoản nhân viên":
    render_account_page()
