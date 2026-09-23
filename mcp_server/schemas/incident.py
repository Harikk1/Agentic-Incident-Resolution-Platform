from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class IncidentRequest(BaseModel):
    incident_id: str

class IncidentResponse(BaseModel):
    incident_id: str
    service: str
    severity: str
    status: str
    symptoms: List[str]
    root_cause: Optional[str] = None
