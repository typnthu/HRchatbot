import streamlit as st
from utils.auth import check_login

def render_account_page():
    col_title, col_user = st.columns([6, 1], gap="small")
    with col_title:
        st.markdown("## 👤 Tài khoản nhân viên")
    with col_user:
        if st.session_state.get("logged_in", False):
            with st.expander(f"👤 {st.session_state['name']}", expanded=False):
                if st.button("🚪 Đăng xuất", key="btn_logout"):
                    for k in ["logged_in", "employeeID", "name", "email", "session_id", "messages", "history"]:
                        st.session_state.pop(k, None)
                    st.rerun()

    if not st.session_state.get("logged_in", False):
        st.markdown("---")
        st.markdown("### 🔐 Đăng nhập")
        with st.form("login_form", clear_on_submit=True):
            emp = st.text_input("Mã nhân viên", key="inp_emp")
            pwd = st.text_input("Mật khẩu", type="password", key="inp_pwd")
            if st.form_submit_button("Đăng nhập"):
                user = check_login(emp, pwd)
                if user:
                    st.session_state.update(
                        {
                            "logged_in": True,
                            "employeeID": user["employeeID"],
                            "name": user.get("emp_name", emp),
                            "email": user.get("email", ""),
                        }
                    )
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Sai employeeID hoặc mật khẩu!")
    else:
        st.success("Bạn đã đăng nhập.")
