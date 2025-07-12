import streamlit as st
import boto3
import pandas as pd
from datetime import date, timedelta



def render_leave_request_page():
    st.title("📄 Quản lý yêu cầu nghỉ phép")

    # Kiểm tra đăng nhập
    if not st.session_state.get("logged_in", False):
        st.warning(
            "Bạn cần đăng nhập trong trang **Tài khoản nhân viên** để xem thông tin nghỉ phép."
        )
        st.stop()

    emp_id = st.session_state["employeeID"]
    today = date.today()

    # Kết nối DynamoDB
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table_request = ddb.Table("leave_request")
    table_emp = ddb.Table("employee_info")

    # Quét leave_request
    try:
        response = table_request.scan()
        items = response.get("Items", [])
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu từ DynamoDB: {e}")
        return

    if not items:
        st.info("Hiện chưa có dữ liệu yêu cầu nghỉ phép.")
        return

    df = pd.DataFrame(items)

    # Đảm bảo cột tồn tại
    expected_columns = [
        "requestID",
        "employeeID",
        "ngay_bat_dau_nghi",
        "ngay_ket_thuc_nghi",
        "so_ngay_nghi",
        "loai_nghi",
        "li_do_xin_nghi",
        "trang_thai",
        "ghi_chu",
        "approverID1",
        "approverID2",
    ]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""

    # Tạo mapping employeeID -> tên
    try:
        emp_resp = table_emp.scan()
        emp_items = emp_resp.get("Items", [])
        employee_map = {
            e["employeeID"]: e.get("emp_name", e["employeeID"]) for e in emp_items
        }
    except Exception as e:
        employee_map = {}
        st.warning("Không lấy được tên nhân viên, sẽ hiển thị mã nhân viên.")

    # Parse ngày và số ngày nghỉ
    df["ngay_bat_dau_nghi_parsed"] = pd.to_datetime(
        df["ngay_bat_dau_nghi"], format="%Y-%m-%d", errors="coerce"
    )
    df["so_ngay_nghi_int"] = pd.to_numeric(df["so_ngay_nghi"], errors="coerce").fillna(
        1
    )

    # ========= PHẦN 1: Yêu cầu của bản thân =========
    st.header("📝 Yêu cầu nghỉ phép của bạn")

    df_self = df[
        (df["employeeID"] == emp_id) & (df["ngay_bat_dau_nghi_parsed"].dt.date >= today)
    ]

    if not df_self.empty:
        df_self_display = df_self.copy()
        df_self_display["Tên nhân viên"] = df_self_display["employeeID"].apply(
            lambda x: employee_map.get(x, x)
        )
        df_self_display = df_self_display.rename(
            columns={
                "requestID": "ID yêu cầu",
                "ngay_bat_dau_nghi": "Ngày bắt đầu",
                "so_ngay_nghi": "Số ngày nghỉ",
                "li_do_xin_nghi": "Lý do nghỉ",
                "trang_thai": "Trạng thái",
                "ghi_chu": "Ghi chú",
            }
        )
        st.dataframe(
            df_self_display[
                [
                    "ID yêu cầu",
                    "Tên nhân viên",
                    "Ngày bắt đầu",
                    "Số ngày nghỉ",
                    "Lý do nghỉ",
                    "Trạng thái",
                    "Ghi chú",
                ]
            ].sort_values(by="Ngày bắt đầu", ascending=True)
        )
    else:
        st.info("Bạn chưa có yêu cầu nghỉ phép nào.")

    # ========= PHẦN 2: Yêu cầu cần duyệt =========
    st.header("✅ Yêu cầu cần bạn duyệt")

    # Tính deadline hiển thị
    def compute_deadline(row):
        if pd.isna(row["ngay_bat_dau_nghi_parsed"]):
            return pd.NaT
        if row["so_ngay_nghi_int"] <= 7:
            return row["ngay_bat_dau_nghi_parsed"].date() - timedelta(days=1)
        else:
            return row["ngay_bat_dau_nghi_parsed"].date() - timedelta(days=3)

    df["deadline_duyet"] = df.apply(compute_deadline, axis=1)

    df_approve = df[
        ((df["approverID1"] == emp_id) | (df["approverID2"] == emp_id))
        & (df["deadline_duyet"] >= today)
    ]

    if df_approve.empty:
        st.info("Không có yêu cầu nào cần bạn duyệt.")
        return

    # Hiển thị từng yêu cầu dưới dạng form
    for idx, row in df_approve.iterrows():
        with st.container():
            ten_nhan_vien = employee_map.get(row["employeeID"], row["employeeID"])
            st.markdown(
                f"### 📝 Đơn nghỉ #{row['requestID']} - Nhân viên {ten_nhan_vien}"
            )
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Ngày bắt đầu", row["ngay_bat_dau_nghi"], disabled=True)
                st.text_input("Số ngày nghỉ", str(row["so_ngay_nghi"]), disabled=True)
            with col2:
                st.text_input("Loại nghỉ", row.get("loai_nghi", ""), disabled=True)
                st.text_input(
                    "Trạng thái hiện tại", row.get("trang_thai", ""), disabled=True
                )
            st.text_area("Lý do nghỉ", row.get("li_do_xin_nghi", ""), disabled=True)
            st.text_area("Ghi chú", row.get("ghi_chu", ""), disabled=True)

            # Quyết định phê duyệt
            action = st.radio(
                f"Chọn hành động cho yêu cầu #{row['requestID']}",
                ["Giữ nguyên", "Phê duyệt", "Từ chối"],
                key=f"action_{row['requestID']}",
            )
            reject_reason = ""
            if action == "Từ chối":
                reject_reason = st.text_area(
                    "Lý do từ chối (bắt buộc)", key=f"reason_{row['requestID']}"
                )

            if st.button("Xác nhận", key=f"confirm_{row['requestID']}"):
                if action == "Từ chối" and not reject_reason.strip():
                    st.error("Vui lòng nhập lý do từ chối!")
                    st.stop()
                if action == "Giữ nguyên":
                    st.info("Bạn chưa chọn phê duyệt hoặc từ chối.")
                    st.stop()

                # Cập nhật DynamoDB
                new_status = "Đã duyệt" if action == "Phê duyệt" else "Đã từ chối"
                try:
                    table_request.update_item(
                        Key={
                            "employeeID": row["employeeID"],
                            "requestID": row["requestID"],
                        },
                        UpdateExpression="SET trang_thai = :s, ghi_chu = :g",
                        ExpressionAttributeValues={
                            ":s": new_status,
                            ":g": reject_reason if action == "Từ chối" else "",
                        },
                    )

                    st.success(f"Đã cập nhật trạng thái thành '{new_status}'.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi cập nhật trạng thái: {e}")
