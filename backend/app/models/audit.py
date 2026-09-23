import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class AuditRecord(BaseModel):
    action_id: str
    incident_id: Optional[str] = None
    actor: str = "AI_AGENT"  # "AI_AGENT" | "USER" | "SYSTEM"
    tool: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk: str = "LOW"  # "LOW" | "MEDIUM" | "HIGH"
    approved: bool = True
    approved_by: Optional[str] = None
    result: str = "SUCCESS"  # "SUCCESS" | "FAILED" | "REJECTED"
    details: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    iso_timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
