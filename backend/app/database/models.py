from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ServiceDocument(BaseModel):
    service_id: str
    name: str
    namespace: str = "smartops"
    status: str = "HEALTHY"
    version: str = "v1.0.0"
    url: str
    desired_replicas: int = 2
    ready_replicas: int = 2
    dependencies: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IncidentDocument(BaseModel):
    incident_id: str
    service: str
    severity: str
    status: str
    title: str
    symptoms: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    rca: Optional[Dict[str, Any]] = None
    recommended_action: Optional[str] = None
    action_parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: Optional[str] = None
    created_at: float
    updated_at: float
    resolved_at: Optional[float] = None
    timeline: List[Dict[str, Any]] = Field(default_factory=list)

class RemediationActionDocument(BaseModel):
    action_id: str
    incident_id: Optional[str] = None
    action: str
    service: str
    parameters: Dict[str, Any]
    status: str
    message: str
    risk: str
    approved: bool
    approved_by: Optional[str] = None
    execution_time_seconds: float
    timestamp: float

class AuditLogDocument(BaseModel):
    action_id: str
    incident_id: Optional[str] = None
    actor: str
    tool: str
    parameters: Dict[str, Any]
    risk: str
    approved: bool
    approved_by: Optional[str] = None
    result: str
    details: Optional[str] = None
    timestamp: float

class KnowledgeBaseDocument(BaseModel):
    doc_id: str
    title: str
    service: str
    symptoms: List[str]
    root_cause: str
    resolution: str
    embedding: Optional[List[float]] = None
    created_at: float

class AgentSessionDocument(BaseModel):
    session_id: str
    user_id: str
    created_at: float
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
