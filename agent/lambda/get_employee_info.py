import boto3
import os
from botocore.exceptions import ClientError
from decimal import Decimal

# Kết nối DynamoDB
dynamodb = boto3.resource("dynamodb")
employee_table_name = os.environ.get("DYNAMO_EMPLOYEE_TABLE_NAME", "employee_info")
leave_request_table_name = os.environ.get("DYNAMO_LEAVE_REQUEST_TABLE_NAME", "leave_request")
employee_table = dynamodb.Table(employee_table_name)
leave_request_table = dynamodb.Table(leave_request_table_name)

def convert_value(key, value):
    if key == "available_leave_days":
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    return value

def sanitize_dynamodb_item(item: dict) -> dict:
    return {k: convert_value(k, v) for k, v in item.items()}

def get_leave_requests(employee_id: str):
    try:
        response = leave_request_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("employeeID").eq(employee_id)
        )
        items = response.get("Items", [])
        # Chuyển đổi các giá trị trong yêu cầu nghỉ phép
        return [
            {
                "requestID": item.get("requestID", ""),
                "employeeID": item.get("employeeID", ""),
                "ngay_bat_dau_nghi": item.get("ngay_bat_dau_nghi", ""),
                "ngay_ket_thuc_nghi": item.get("ngay_ket_thuc_nghi", ""),
                "so_ngay_nghi": convert_value("so_ngay_nghi", item.get("so_ngay_nghi", 0)),
                "loai_nghi": item.get("loai_nghi", ""),
                "li_do_xin_nghi": item.get("li_do_xin_nghi", ""),
                "trang_thai": item.get("trang_thai", ""),
                "ghi_chu": item.get("ghi_chu", "")
            }
            for item in items
        ]
    except ClientError as e:
        raise Exception(f"DynamoDB ClientError while querying leave requests: {e.response['Error']['Message']}")

def get_employee_info(employee_id: str, current_employee_id: str) -> dict:
    if employee_id != current_employee_id:
        raise PermissionError("You do not have permission to view this employee's information.")

    try:
        # Truy vấn thông tin nhân viên từ bảng `employee_info`
        response = employee_table.get_item(Key={"employeeID": employee_id})
        item = response.get("Item")
        
        if not item:
            return {
                "employeeID": employee_id,
                "password": "",
                "emp_name": "",
                "position": "",
                "managerID": "",
                "manager_email": "",
                "department": "",
                "email": "",
                "current_project": "",
                "project_managerID": "",
                "project_manager_email": "",
                "available_leave_days": 0,
                "leave_requests": []
            }

        # Lấy thông tin yêu cầu nghỉ phép
        leave_requests = get_leave_requests(employee_id)

        # Trả về thông tin nhân viên kết hợp với yêu cầu nghỉ phép
        return {
            **sanitize_dynamodb_item(item),
            "leave_requests": leave_requests
        }

    except ClientError as e:
        raise Exception(f"DynamoDB ClientError: {e.response['Error']['Message']}")
