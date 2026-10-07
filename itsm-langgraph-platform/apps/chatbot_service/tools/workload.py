# apps/chatbot_service/tools/pending.py
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from apps.chatbot_service.integrations.itsm_client import ITSMClient

@tool
async def get_my_workload(config: RunnableConfig) -> str:
    """
    PRIMARY TOOL for all workload.
    Fetch ALL workload items (both incidents AND requests).
    Use this tool whenever the user asks:
    - "Show my workload"
    - "What is my workload?"
    - "Show all my items"
    - "Show my pending work"
    """
    
    auth_token = config.get("configurable", {}).get("user_token")
    client = ITSMClient()
    try:
        data = await client.get_my_workload(auth_token=auth_token)
        incidents = data.get("incidents", [])
        requests = data.get("requests", [])
        print(f"-> Found {len(incidents)} Incidents, {len(requests)} Requests")

        output = []
        if incidents:
            output.append("### workload Incidentss:")
            for inc in incidents:
                output.append(f"- Incident {inc.get('incident_number')}: {inc.get('title')} (Status: {inc.get('status')})")

        if requests:
            output.append("### workload Requests:")
            for req in requests:
                output.append(f"- Request {req.get('request_number')}: {req.get('title')} (Status: {req.get('status')})")

        return "\n".join(output) if output else "No workload items found."
    except Exception as e:
        return f"Error: {str(e)}"