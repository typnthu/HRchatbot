import boto3
from .logger import logger

AGENT_ID = "RYF1TLCK1H"
AGENT_ALIAS_ID = "T9FWJKTCBK"
REGION = "us-east-1"

def call_bedrock_agent(query, session_id, employee_id):
    client = boto3.client("bedrock-agent-runtime", region_name=REGION)
    payload = {
        "agentId": AGENT_ID,
        "agentAliasId": AGENT_ALIAS_ID,
        "sessionId": session_id,
        "inputText": query,
        "endSession": False,
        "sessionState": {
            "promptSessionAttributes": {"employeeID": employee_id},
            "sessionAttributes": {"employeeID": employee_id},
        },
    }
    try:
        logger.info(f"Calling Bedrock Agent with session_id: {session_id}, employee_id: {employee_id}, query: {query}")
        resp = client.invoke_agent(**payload)
        out = ""
        for ev in resp["completion"]:
            if "chunk" in ev and "bytes" in ev["chunk"]:
                out += ev["chunk"]["bytes"].decode("utf-8")
            elif "output" in ev:
                out += ev["output"]
        logger.info(f"Bedrock Agent response: {out}")
        return out
    except Exception as e:
        logger.error(f"Error calling Bedrock Agent: {str(e)}")
        return "Đã xảy ra sự cố khi xử lý yêu cầu. Vui lòng thử lại sau."
