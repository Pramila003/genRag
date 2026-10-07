from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Assignee(BaseModel):
    user_id: str
    name: str
    email: str

class IncidentDocument(BaseModel):
    incident_number: str
    tenant_id: str
    title: str
    description: str
    status: str = "In Progress"     
    is_active: bool = True
    priority: str = "P2 - High"
    urgency: str = "High"
    assigned_to: Optional[Assignee] = None
    latest_comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)