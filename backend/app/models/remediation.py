from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class RemediationActionType(str, Enum):
    RESTART_SERVICE = "restart_service"
    RESTART_POD = "restart_pod"
    SCALE_SERVICE = "scale_service"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    INCREASE_RESOURCES = "increase_resources"
    CLEANUP_DISK = "cleanup_disk"
    SCALE_CONSUMERS = "scale_consumers"
    VERIFY_SERVICE_HEALTH = "verify_service_health"

class RemediationPlan(BaseModel):
    action: RemediationActionType
    service: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel
    reason: str
    expected_outcome: str

class ApprovalDecision(BaseModel):
    decision: str  # "APPROVE" | "REJECT"
    comments: Optional[str] = None
    approved_by: str = "engineer@smartops.ai"

class RemediationExecutionResult(BaseModel):
    action_id: str
    incident_id: Optional[str] = None
    action: RemediationActionType
    service: str
    parameters: Dict[str, Any]
    status: str  # "SUCCESS" | "PARTIAL_SUCCESS" | "FAILED"
    message: str
    health_verified: bool = False
    verification_details: Dict[str, Any] = Field(default_factory=dict)
    execution_time_seconds: float = 0.0
