from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ToolExecutionTrace(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    status: str = "COMPLETED"  # RUNNING | COMPLETED | FAILED
    result_summary: str
    timestamp: float

class AgentState(BaseModel):
    current_step: str = "UNDERSTAND_REQUEST"
    user_request: str
    service: Optional[str] = None
    incident_id: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: List[Dict[str, Any]] = Field(default_factory=list)
    historical_incidents: List[Dict[str, Any]] = Field(default_factory=list)
    anomaly_results: Dict[str, Any] = Field(default_factory=dict)
    rca_result: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    action_parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "LOW"  # LOW | MEDIUM | HIGH
    approval_status: str = "PENDING"  # PENDING | APPROVED | REJECTED | NOT_REQUIRED
    approval_card: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    verification_result: Optional[Dict[str, Any]] = None
    final_response: str = ""
    tool_traces: List[ToolExecutionTrace] = Field(default_factory=list)
