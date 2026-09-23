from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ServiceMetricRequest(BaseModel):
    service: str

class ServiceMetricResponse(BaseModel):
    service: str
    status: str
    metrics: Dict[str, Any]
