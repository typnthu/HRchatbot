import json
import boto3
import uuid
from botocore.exceptions import ClientError
import logging
from decimal import Decimal
from date_utils import validate_date

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
ses_client = boto3.client("ses")

employee_table = dynamodb.Table("employee_info")
leave_request_table = dynamodb.Table("leave_request")


def is_valid_email(email):
    return isinstance(email, str) and "@" in email


def convert_value(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    return value


def sanitize_item(item):
    return {k: convert_value(v) for k, v in item.items()}


def send_email(to_addresses, subject, body, cc_addresses=None):
    if cc_addresses is None:
        cc_addresses = []
    try:
        ses_client.send_email(
            Source="email@source",
            Destination={"ToAddresses": to_addresses, "CcAddresses": cc_addresses},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
        )
        logger.info(f"Đã gửi email đến {to_addresses}")
    except ClientError as e:
        logger.error(f"Không gửi được email: {e.response['Error']['Message']}")
        raise


def create_leave_request(data):
    logger.info("Dữ liệu yêu cầu create: %s", json.dumps(data, ensure_ascii=False))
    try:
        employee_id = data.get("employeeID")
        if not employee_id:
            return {"error": "Thiếu employeeID."}, 400

        start_date = validate_date(data.get("ngay_bat_dau_nghi"))
        end_date = validate_date(data.get("ngay_ket_thuc_nghi"))
        if start_date > end_date:
            return {"error": "Ngày bắt đầu phải trước hoặc bằng ngày kết thúc."}, 400

        so_ngay_nghi = data.get("so_ngay_nghi")
        if not so_ngay_nghi:
            so_ngay_nghi = (end_date - start_date).days + 1

        resp = employee_table.get_item(Key={"employeeID": employee_id})
        emp = resp.get("Item")
        if not emp:
            return {"error": "Không tìm thấy nhân viên."}, 400

        emp = sanitize_item(emp)
        available_leave = int(emp.get("available_leave_days", 0))
        if Decimal(str(so_ngay_nghi)) > Decimal(str(available_leave)):
            return {"error": "Không đủ ngày phép."}, 400

        request_id = str(uuid.uuid4())

        # Tạo leave_item cơ bản
        leave_item = {
            "requestID": request_id,
            "employeeID": employee_id,
            "ngay_bat_dau_nghi": str(start_date),
            "ngay_ket_thuc_nghi": str(end_date),
            "so_ngay_nghi": Decimal(str(so_ngay_nghi)),
            "loai_nghi": data.get("loai_nghi"),
            "li_do_xin_nghi": data.get("li_do_xin_nghi"),
            "trang_thai": "Chờ duyệt",
            "ghi_chu": "",
            "approverID1": emp.get("managerID", ""),
        }

        # Kiểm tra project_manager_email có tồn tại và không trùng email nhân viên
        project_manager_id = emp.get("project_managerID", "")
        project_manager_email = emp.get("project_manager_email")
        employee_email = emp.get("email")

        if (
            project_manager_email
            and is_valid_email(project_manager_email)
            and project_manager_email.strip().lower() != (employee_email or "").strip().lower()
        ):
            leave_item["approverID2"] = project_manager_id

        leave_request_table.put_item(Item=leave_item)

        # Lấy thông tin email
        manager_email = emp.get("manager_email")
        valid_manager_email = is_valid_email(manager_email)
        valid_project_email = is_valid_email(project_manager_email)
        valid_employee_email = is_valid_email(employee_email)

        to_addresses = []
        cc_addresses = []

        if valid_manager_email and valid_project_email:
            if manager_email.strip().lower() == project_manager_email.strip().lower():
                to_addresses.append(manager_email)
            else:
                to_addresses.append(manager_email)
                cc_addresses.append(project_manager_email)
        elif valid_manager_email:
            to_addresses.append(manager_email)
        elif valid_project_email:
            to_addresses.append(project_manager_email)
        else:
            return {"error": "Không tìm thấy email quản lý hợp lệ."}, 400

        if valid_employee_email:
            cc_addresses.append(employee_email)

        # Chuẩn bị thông tin bổ sung
        ma_nv = employee_id
        ten_nv = emp.get("emp_name", "Chưa có tên")
        phong_ban = emp.get("department", "Không rõ")

        du_an = emp.get("current_project")
        truong_du_an_ten = None

        # Nếu có ID trưởng dự án, tra cứu bảng employee_info để lấy tên
        if project_manager_id:
            pm_resp = employee_table.get_item(Key={"employeeID": project_manager_id})
            pm_item = pm_resp.get("Item")
            if pm_item:
                truong_du_an_ten = pm_item.get("emp_name")

        if du_an:
            du_an_info = f"- Dự án hiện tại: {du_an}\n"
            truong_du_an_info = (
                f"- Trưởng dự án hiện tại: {truong_du_an_ten}\n" if truong_du_an_ten else ""
            )
        else:
            du_an_info = ""
            truong_du_an_info = ""

        # Subject và body email
        subject = "Yêu cầu nghỉ phép của nhân viên"

        body = (
            f"Yêu cầu nghỉ phép của nhân viên:\n\n"
            f"- Mã nhân viên: {ma_nv}\n"
            f"- Tên nhân viên: {ten_nv}\n"
            f"- Phòng ban: {phong_ban}\n"
            f"{du_an_info}"
            f"{truong_du_an_info}"
            f"- Thời gian nghỉ: Từ {start_date} đến {end_date}\n"
            f"- Số ngày: {so_ngay_nghi}\n"
            f"- Lý do: {data.get('li_do_xin_nghi')}\n\n"
            "Vui lòng đăng nhập hệ thống để duyệt yêu cầu."
        )

        send_email(to_addresses, subject, body, cc_addresses)

        return {
            "message": f"Yêu cầu nghỉ {so_ngay_nghi} ngày đã được gửi thành công.",
            "leave_request": leave_item,
        }, 200

    except Exception as e:
        logger.exception("Lỗi xử lý yêu cầu nghỉ phép")
        return {"error": f"Lỗi hệ thống: {str(e)}"}, 500
