from get_employee_info import get_employee_info
from leave_request import create_leave_request
from aws_lambda_powertools import Logger
from decimal import Decimal
import json

logger = Logger()

def default_serializer(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"{type(obj)} is not JSON serializable")

def handler(event, context):
    # Log RAW EVENT
    logger.info("=== RAW EVENT ===")
    logger.info(json.dumps(event, ensure_ascii=False))

    try:
        api_path = event.get("apiPath", "")

        request_body = event.get("requestBody")
        if request_body:
            props = (
                request_body
                .get("content", {})
                .get("application/json", {})
                .get("properties", [])
            )
            data = {p["name"]: p["value"] for p in props}
        else:
            data = {}

        # Log request data
        logger.info("=== REQUEST DATA ===")
        logger.info(json.dumps(data, ensure_ascii=False))

        current_employee_id = event.get("sessionAttributes", {}).get("employeeID", "")
        if not current_employee_id:
            raise PermissionError("No employee ID found in session.")

        if api_path == "/get_employee_info":
            employee_id = data.get("employeeID") or current_employee_id
            result = get_employee_info(employee_id, current_employee_id)
            http_status = 200

        elif api_path == "/leave_request":
            if not data:
                return {
                    "messageVersion": "1.0",
                    "response": {
                        "actionGroup": event.get("actionGroup"),
                        "apiPath": api_path,
                        "httpMethod": event.get("httpMethod"),
                        "httpStatusCode": 400,
                        "responseBody": {
                            "application/json": {
                                "body": json.dumps({
                                    "error": "Missing leave request data."
                                })
                            }
                        }
                    }
                }

            if data.get("employeeID") != current_employee_id:
                raise PermissionError("You can only create leave requests for yourself.")
            result, http_status = create_leave_request(data)
        else:
            raise Exception(f"Unknown API path: {api_path}")

        if http_status == 400:
            body = {
                "application/json": {
                    "body": json.dumps(result)
                }
            }
        else:
            body = {
                "application/json": {
                    "body": json.dumps(result, default=default_serializer)
                }
            }

        action_response = {
            "actionGroup": event.get("actionGroup"),
            "apiPath": api_path,
            "httpMethod": event.get("httpMethod"),
            "httpStatusCode": http_status,
            "responseBody": body
        }

        # Log response thành công
        logger.info("=== RESPONSE ===")
        logger.info(json.dumps(action_response, ensure_ascii=False, indent=2))

        return {
            "messageVersion": "1.0",
            "response": action_response,
            "sessionAttributes": event.get("sessionAttributes", {}),
            "promptSessionAttributes": event.get("promptSessionAttributes", {})
        }

    except Exception as e:
        logger.exception("Error in Lambda handler")

        error_body = {
            "application/json": {
                "body": json.dumps({
                    "error": "Failed to handle request",
                    "detail": str(e)
                }, ensure_ascii=False)
            }
        }
        action_response = {
            "actionGroup": event.get("actionGroup"),
            "apiPath": event.get("apiPath"),
            "httpMethod": event.get("httpMethod"),
            "httpStatusCode": 500,
            "responseBody": error_body
        }

        logger.error("=== ERROR RESPONSE ===")
        logger.error(json.dumps(action_response, ensure_ascii=False, indent=2))

        return {
            "messageVersion": "1.0",
            "response": action_response,
            "sessionAttributes": event.get("sessionAttributes", {}),
            "promptSessionAttributes": event.get("promptSessionAttributes", {})
        }
