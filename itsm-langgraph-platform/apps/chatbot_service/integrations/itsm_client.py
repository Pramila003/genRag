# apps/chatbot_service/integrations/itsm_client.py
import httpx
from typing import Optional, Dict, Any
from apps.chatbot_service.core.config import settings

class ITSMClient:
    def __init__(self, base_url: Optional[str] = None):
        # Uses settings.ITSM_API_BASE_URL by default, but allows overrides (e.g., in unit tests)
        self.base_url = (base_url or settings.ITSM_API_BASE_URL).rstrip("/")

    async def get_incident(self, incident_number: str, auth_token: str) -> Optional[Dict[str, Any]]:
        """Makes an authenticated GET request to the ITSM backend."""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/incidents/{incident_number.upper()}",
                headers=headers
            )
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            return response.json()

    async def get_all_incidents(self, auth_token: str)-> Dict:
            """Calls GET /api/v1/me/incidents on the ITSM Backend."""
            headers = {"Authorization": f"Bearer {auth_token}"}
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    f"{self.base_url}/me/incidents",
                    headers=headers
                )
                if res.status_code == 404:
                    return None
                res.raise_for_status()
                return res.json()

    async def get_my_requests(self, auth_token: str, status: Optional[str] = None) -> Dict[str, Any]:
        """Calls the ITSM endpoint to retrieve all requests for the authenticated user."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        params = {}
        if status:
            params["status"] = status
            
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{self.base_url}/me/requests",
                headers=headers,
                params=params
            )
            res.raise_for_status()
            return res.json()
        
    async def get_request_by_number(self, request_number: str, auth_token: str) -> Optional[Dict[str, Any]]:
        """Calls the backend to get details for one specific request."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{self.base_url}/requests/{request_number.upper()}",
                headers=headers
            )
            if res.status_code == 404:
                return None
            res.raise_for_status()
            return res.json()



    async def get_my_pending_approvals(self, auth_token: str)-> Dict:
        """Calls GET /api/v1/me/pending-items on the ITSM Backend."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{self.base_url}/me/pending-items",
                headers=headers
            )
            if res.status_code == 404:
                return None
            res.raise_for_status()
            return res.json()

    async def get_my_workload(self, auth_token: str)-> Dict:
            """Calls GET /api/v1/me/workload on the ITSM Backend."""
            headers = {"Authorization": f"Bearer {auth_token}"}
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    f"{self.base_url}/me/workload",
                    headers=headers
                )
                if res.status_code == 404:
                    return None
                res.raise_for_status()
                return res.json()