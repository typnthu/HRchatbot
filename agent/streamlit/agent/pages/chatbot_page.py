import streamlit as st
from utils.bedrock import call_bedrock_agent

def render_chatbot_page():
    st.title("🤖 Chatbot Nhân sự")

    if not st.session_state.get("logged_in", False):
        st.warning("Bạn cần đăng nhập trong trang **Tài khoản nhân viên** để sử dụng chatbot.")
        st.stop()

    # Khởi tạo session
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = st.session_state["employeeID"]
    if "messages" not in st.session_state:
        # Khởi tạo tin nhắn mặc định khi mới bắt đầu
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Chào mừng bạn đến với chatbot của NexusTech. Bạn cần tôi giúp gì nào?"
            }
        ]

    # Hiển thị lịch sử tin nhắn
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Ô nhập câu hỏi dưới cùng
    if prompt := st.chat_input("Nhập câu hỏi tại đây"):
        # Hiển thị tin nhắn người dùng
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Gọi agent
        with st.spinner("Agent đang xử lý..."):
            reply = call_bedrock_agent(
                prompt,
                st.session_state["session_id"],
                st.session_state["employeeID"]
            )

        # Hiển thị phản hồi
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

    # Thêm khoảng trắng cuối trang để không bị che
    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
