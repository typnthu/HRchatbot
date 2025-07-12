import boto3
import streamlit as st

REGION = "us-east-1"
DYNAMO_TABLE = "employee_info"

def check_login(employee_id, password):
    ddb = boto3.resource("dynamodb", region_name=REGION)
    table = ddb.Table(DYNAMO_TABLE)
    try:
        r = table.get_item(Key={"employeeID": employee_id})
        user = r.get("Item")
        if user and user.get("password") == password:
            return user
    except Exception as e:
        st.error(f"Lỗi truy vấn DynamoDB: {e}")
    return None
