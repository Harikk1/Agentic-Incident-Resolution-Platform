import time
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class IncidentSeverity(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IncidentState(str, Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    DIAGNOSED = "DIAGNOSED"
    REMEDIATION_PROPOSED = "REMEDIATION_PROPOSED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    REMEDIATION_EXECUTING = "REMEDIATION_EXECUTING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    REMEDIATION_FAILED = "REMEDIATION_FAILED"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"

class RootCause(str, Enum):
    TRAFFIC_SPIKE = "TRAFFIC_SPIKE"
    DATABASE_BOTTLENECK = "DATABASE_BOTTLENECK"
    MEMORY_LEAK = "MEMORY_LEAK"
    BAD_DEPLOYMENT = "BAD_DEPLOYMENT"
    SERVICE_FAILURE = "SERVICE_FAILURE"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    CPU_SATURATION = "CPU_SATURATION"
    DISK_PRESSURE = "DISK_PRESSURE"
    QUEUE_BACKLOG = "QUEUE_BACKLOG"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    EXTERNAL_API_FAILURE = "EXTERNAL_API_FAILURE"
    UNKNOWN = "UNKNOWN"

class RCAResult(BaseModel):
    root_cause: RootCause = RootCause.UNKNOWN
    confidence: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    contributing_factors: List[str] = Field(default_factory=list)

class IncidentTimelineEvent(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    from_state: Optional[str] = None
    to_state: str
    actor: str = "SYSTEM"  # SYSTEM | AI_AGENT | USER
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

class Incident(BaseModel):
    incident_id: str
    service: str
    severity: IncidentSeverity = IncidentSeverity.HIGH
    status: IncidentState = IncidentState.DETECTED
    title: str
    symptoms: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    rca: Optional[RCAResult] = None
    recommended_action: Optional[str] = None
    action_parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: Optional[str] = None  # LOW | MEDIUM | HIGH
    approval_required: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[float] = None
    remediation_result: Optional[str] = None
    verification_result: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    resolved_at: Optional[float] = None
    timeline: List[IncidentTimelineEvent] = Field(default_factory=list)
