from fastapi import APIRouter, Depends, HTTPException, Header
from apps.itsm_service.models.incident import IncidentDocument
from apps.itsm_service.repositories.incident_repo import IncidentRepository

router = APIRouter()

# Dependency to extract tenant/user from JWT
def get_current_tenant(authorization: str = Header(...)) -> str:
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
   
    return "tenant_abc_123"

@router.get("/incidents/{incident_number}", response_model=IncidentDocument)
async def get_incident(
    incident_number: str,
    tenant_id: str = Depends(get_current_tenant),
    # Assume db is provided via FastAPI dependency
    # db = Depends(get_database)
):
    from apps.itsm_service.main import db_instance
    repo = IncidentRepository(db_instance.db)
    
    incident = await repo.get_by_incident_number(incident_number, tenant_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_number} not found.")
    
    return incident