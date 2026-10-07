# apps/chatbot_service/tools/pending.py
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from apps.chatbot_service.integrations.itsm_client import ITSMClient

@tool
async def get_my_pending_items(config: RunnableConfig) -> str:
    """
    PRIMARY TOOL for all pending work.
    Fetch ALL pending items (both incidents AND requests).
    Use this tool whenever the user asks:
    - "Show my pending work"
    - "What is pending for me?"
    - "Show all pending items"
    - "Show my approvals"
    """
    print("\n🚨 [TOOL CALLED]: get_my_pending_items")
    auth_token = config.get("configurable", {}).get("user_token")
    client = ITSMClient()
    try:
        data = await client.get_my_pending_items(auth_token=auth_token)
        incidents = data.get("incidents", [])
        requests = data.get("requests", [])
        print(f"-> Found {len(incidents)} Incidents, {len(requests)} Requests")

        output = []
        if incidents:
            output.append("### Pending Incidents:")
            for inc in incidents:
                output.append(f"- Incident {inc.get('incident_number')}: {inc.get('title')} (Status: {inc.get('status')})")

        if requests:
            output.append("### Pending Requests:")
            for req in requests:
                output.append(f"- Request {req.get('request_number')}: {req.get('title')} (Status: {req.get('status')})")

        return "\n".join(output) if output else "No pending items found."
    except Exception as e:
        return f"Error: {str(e)}"