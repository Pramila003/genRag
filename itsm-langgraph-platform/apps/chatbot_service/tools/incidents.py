from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from apps.chatbot_service.integrations.itsm_client import ITSMClient

@tool
async def get_incident(incident_number: str, config: RunnableConfig) -> str:
    """
    Fetch active/live details of an IT incident by its number (e.g., 'INC10234').
    Use this tool whenever a user asks about the status, priority, description, or updates on an incident.

    Args:
        incident_number: Unique ID of the incident (e.g. 'INC10234').
    """
    # 1. Retrieve the JWT injected into LangGraph's config
    auth_token = config.get("configurable", {}).get("user_token")
    if not auth_token:
        return "Error: Missing authentication token. Please log in."

    client = ITSMClient()
    try:
        data = await client.get_incident(incident_number=incident_number, auth_token=auth_token)
        if not data:
            return f"No incident found matching number '{incident_number.upper()}'."

        # 2. Check if active
        status = data.get("status", "Unknown")
        is_active = data.get("is_active", True)
        if status in ["Closed", "Resolved", "Cancelled"] or not is_active:
            return (
                f"Incident {incident_number.upper()} is currently INACTIVE ({status}). "
                f"Title: {data.get('title')}. "
                f"Last updated: {data.get('updated_at')}."
            )

        # 3. Format structured output for LLM synthesis
        assignee = data.get("assigned_to") or {}
        return (
            f"Incident: {data.get('incident_number')}\n"
            f"- Title: {data.get('title')}\n"
            f"- Status: {status} (Active)\n"
            f"- Priority: {data.get('priority')}\n"
            f"- Urgency: {data.get('urgency')}\n"
            f"- Assigned To: {assignee.get('name', 'Unassigned')}\n"
            f"- Latest Comment: {data.get('latest_comment', 'No comments')}\n"
            f"- Description: {data.get('description')}\n"
            f"- Created At: {data.get('created_at')}"
        )
    except Exception as e:
        return f"Failed to retrieve incident {incident_number}: {str(e)}"


@tool
async def get_my_incident(config: RunnableConfig) -> str:
    """
    Fetch all IT service incidents (tickets) submitted/created by the current user.
    Use this tool when the user asks:
    - "Show all my incidents"
    - "What tickets did I open?"
    - "Show my pending incidents"

    Args:
        status: (Optional) Filter requests by status like 'In Progress', 'Pending Approval', 'Completed', or None for all.
    """
    print("\n🚨 [TOOL CALLED]: get_my_incidents")
    auth_token = config.get("configurable", {}).get("user_token")
    if not auth_token:
        return "Error: Missing authentication token. Please log in."

    client = ITSMClient()
    try:
        data = await client.get_my_incidents(auth_token=auth_token)
        incidents = data.get("incidents", [])
        
      
        # Format clean list for the LLM
        output = [f"Found {len(incidents)} incident(s):"]
        for idx, incident in enumerate(incidents, 1):
            output.append(
                f"{idx}. [{incident.get('incident_number')}] {incident.get('title')}\n"
                f"   - Category: {incident.get('category', 'General')}\n"
                f"   - Status: {incident.get('status')}\n"
                f"   - Details: {incident.get('description')}"
            )
            
        return "\n".join(output)
        
    except Exception as e:
        return f"Failed to fetch your incidents: {str(e)}"