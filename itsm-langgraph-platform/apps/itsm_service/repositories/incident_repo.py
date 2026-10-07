from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class IncidentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["incidents"]

    async def get_by_incident_number(self, incident_number: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({
            "incident_number": incident_number.upper(),
            "tenant_id": tenant_id
        })
    