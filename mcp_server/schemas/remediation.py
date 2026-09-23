from pydantic import BaseModel
from typing import Dict, Any, Optional

class ScaleServiceRequest(BaseModel):
    service: str
    replicas: int

class RemediationToolResponse(BaseModel):
    status: str
    message: str
    service: str
    action: str
    health_verified: bool = False
