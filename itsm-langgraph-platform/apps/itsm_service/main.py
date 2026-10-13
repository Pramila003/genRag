# apps/itsm_service/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Optional
from apps.itsm_service.models.incident import IncidentDocument
from apps.itsm_service.repositories.incident_repo import IncidentRepository

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "itsm_database")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    db_instance.client = AsyncIOMotorClient(MONGO_URI)
    db_instance.db = db_instance.client[DB_NAME]
    print(f" Connected to MongoDB at '{DB_NAME}'")
    yield
    # Shutdown: Close MongoDB Connection
    if db_instance.client:
        db_instance.client.close()
        print("🔌 MongoDB connection closed")

# --- FastAPI Instance (This is what Uvicorn looks for) ---
app = FastAPI(
    title="ITSM Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# --- Auth Helper ---
def get_current_tenant(authorization: str = Header(...)) -> str:
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing token")
    # For testing, returns tenant ID
    return "tenant_abc_123"

def get_current_user_and_tenant(authorization: str = Header(...)) -> dict:
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing token")
    
    # For testing: returns tenant_id and user_id (In production, decoded from JWT)
    return {
        "tenant_id": "tenant_abc_123",
        "user_id": "usr_104"
    }

# --- Incident Endpoint ---
@app.get("/api/v1/incidents/{incident_number}", response_model=IncidentDocument)
async def get_incident(
    incident_number: str,
    tenant_id: str = Depends(get_current_tenant)
):
    repo = IncidentRepository(db_instance.db)
    incident = await repo.get_by_incident_number(incident_number, tenant_id)
    
    if not incident:
        raise HTTPException(
            status_code=404, 
            detail=f"Incident {incident_number} not found"
        )
    
    return incident


@app.get("/api/v1/me/incident")
async def get_my_all_incident(auth_ctx: dict = Depends(get_current_user_and_tenant)):
        tenant_id = auth_ctx["tenant_id"]
        user_id = auth_ctx["user_id"]
        incidents_query = {
            "tenant_id": tenant_id,
            "is_active": True,
            "assigned_to.user_id": user_id
        }
        incidents_cursor = db_instance.db["incidents"].find(incidents_query)
        incidents_list = await incidents_cursor.to_list(length=50)
        for item in incidents_list:
            item["_id"] = str(item["_id"])
        return {
            "total_incidents": len(incidents_list),
            "incidents": incidents_list
        }
   
  

@app.get("/api/v1/me/requests")
async def get_my_requests_endpoint(
    status: Optional[str] = None,
    auth_ctx: dict = Depends(get_current_user_and_tenant)
):
    """Fetches all service requests created by the authenticated user."""
    query = {
        "tenant_id": auth_ctx["tenant_id"],
        "requester_id": auth_ctx["user_id"]
    }
    
    # Apply optional status filter (case-insensitive)
    if status and status.lower() != "all":
        query["status"] = {"$regex": f"^{status}$", "$options": "i"}
        
    cursor = db_instance.db["request"].find(query).sort("created_at", -1)
    requests_list = await cursor.to_list(length=100)
    
    # Convert MongoDB ObjectId to string
    for req in requests_list:
        req["_id"] = str(req["_id"])
        
    return {"count": len(requests_list), "requests": requests_list}

@app.get("/api/v1/requests/{request_number}")
async def get_single_request_endpoint(
    request_number: str,
    auth_ctx: dict = Depends(get_current_user_and_tenant)
):
    """Finds a single request by its number (e.g. REQ1001)."""
    doc = await db_instance.db["request"].find_one({
        "request_number": request_number.upper(),
        "tenant_id": auth_ctx["tenant_id"]
    })
    
    if not doc:
        raise HTTPException(
            status_code=404, 
            detail=f"Request {request_number} not found."
        )
        
    doc["_id"] = str(doc["_id"])
    return doc



@app.get("/api/v1/me/pending-items")
async def get_my_pending_items_endpoint(
    auth_ctx: dict = Depends(get_current_user_and_tenant)
):
    tenant_id = auth_ctx["tenant_id"]   
    user_id = auth_ctx["user_id"]    

    incidents_query = {
        "tenant_id": tenant_id,
        "is_active": True,
        "status": {"$in": ["Pending"]},
        "assigned_to.user_id": user_id  
    }
    
    
    requests_query = {
        "tenant_id": tenant_id,
        "requester_id": user_id,
        "status": {"$in": ["Pending Approval"]}
    }

    
    incidents_cursor = db_instance.db["incidents"].find(incidents_query)
    requests_cursor = db_instance.db["request"].find(requests_query)

    incidents_list = await incidents_cursor.to_list(length=50)
    requests_list = await requests_cursor.to_list(length=50)


    
    for item in incidents_list:
        item["_id"] = str(item["_id"])
    for item in requests_list:
        item["_id"] = str(item["_id"])

    return {
        "total_pending": len(incidents_list) + len(requests_list),
        "incidents": incidents_list,
        "requests": requests_list
    }

@app.get("/api/v1/me/workload")
async def get_my_workload(
    auth_ctx: dict = Depends(get_current_user_and_tenant)
):
    tenant_id = auth_ctx["tenant_id"]   
    user_id = auth_ctx["user_id"]    

    incidents_query = {
        "tenant_id": tenant_id,
        "is_active": True,
        "status": {"$in": ["Pending", "In Progress"]},
        "assigned_to.user_id": user_id  
    }
    
    
    requests_query = {
        "tenant_id": tenant_id,
        "requester_id": user_id,
        "status": {"$in": ["Pending Approval", "In Progress"]}
    }

    
    incidents_cursor = db_instance.db["incidents"].find(incidents_query)
    requests_cursor = db_instance.db["request"].find(requests_query)

    incidents_list = await incidents_cursor.to_list(length=50)
    requests_list = await requests_cursor.to_list(length=50)


    
    for item in incidents_list:
        item["_id"] = str(item["_id"])
    for item in requests_list:
        item["_id"] = str(item["_id"])

    return {
        "total_workload": len(incidents_list) + len(requests_list),
        "incidents": incidents_list,
        "requests": requests_list
    }
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "itsm_service"}