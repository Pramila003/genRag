# apps/chatbot_service/tools/requests.py
from typing import Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from apps.chatbot_service.integrations.itsm_client import ITSMClient

@tool
async def get_my_requests(config: RunnableConfig, status: Optional[str] = None) -> str:
    """
    Fetch all IT service requests (tickets) submitted/created by the current user.
    Use this tool when the user asks:
    - "Show all my requests"
    - "What tickets did I open?"
    - "Show my pending requests"
    
    Args:
        status: (Optional) Filter requests by status like 'In Progress', 'Pending Approval', 'Completed', or None for all.
    """
    print("\n🚨 [TOOL CALLED]: get_my_requests")
    auth_token = config.get("configurable", {}).get("user_token")
    if not auth_token:
        return "Error: Missing authentication token. Please log in."

    client = ITSMClient()
    try:
        data = await client.get_my_requests(auth_token=auth_token, status=status)
        requests = data.get("requests", [])
        
        if not requests:
            filter_msg = f" with status '{status}'" if status else ""
            return f"You currently have no service requests{filter_msg}."

        # Format clean list for the LLM
        output = [f"Found {len(requests)} request(s):"]
        for idx, req in enumerate(requests, 1):
            output.append(
                f"{idx}. [{req.get('request_number')}] {req.get('title')}\n"
                f"   - Category: {req.get('category', 'General')}\n"
                f"   - Status: {req.get('status')}\n"
                f"   - Details: {req.get('description')}"
            )
            
        return "\n".join(output)
        
    except Exception as e:
        return f"Failed to fetch your requests: {str(e)}"

@tool
async def get_request(request_number: str, config: RunnableConfig) -> str:
    """
    Fetch full details of a specific service request by its request number (e.g., 'REQ1001', 'REQ1002').
    Use this tool whenever the user asks about a specific request ticket number.
    show ticket number 

    Args:
        request_number: The unique ID of the request (e.g. 'REQ1001').
    """
    auth_token = config.get("configurable", {}).get("user_token")
    if not auth_token:
        return "Error: Missing authentication token. Please log in."

    client = ITSMClient()
    try:
        data = await client.get_request_by_number(request_number=request_number, auth_token=auth_token)
        if not data:
            return f"No service request found with number '{request_number.upper()}'."

        # Format details cleanly for the LLM
        return (
            f"Service Request Details:\n"
            f"- Request Number: {data.get('request_number')}\n"
            f"- Title: {data.get('title')}\n"
            f"- Category: {data.get('category', 'General')}\n"
            f"- Status: {data.get('status')}\n"
            f"- Requested By: {data.get('requester_name', 'N/A')}\n"
            f"- Description: {data.get('description', 'No description provided')}\n"
            f"- Created At: {data.get('created_at', 'N/A')}"
        )
    except Exception as e:
        return f"Failed to retrieve request {request_number}: {str(e)}"