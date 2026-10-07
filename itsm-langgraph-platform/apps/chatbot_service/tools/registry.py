from apps.chatbot_service.tools.incidents import get_incident,get_my_incident
from apps.chatbot_service.tools.pending import get_my_pending_items
from apps.chatbot_service.tools.requests import get_my_requests,get_request
from apps.chatbot_service.tools.workload import get_my_workload
ALL_TOOLS = [
    get_my_pending_items,
    get_incident,
    get_my_requests,
    get_request,
    get_my_workload,
    get_my_incident
    
    
]