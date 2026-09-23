from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.models.incident import Incident, IncidentState, IncidentSeverity
from backend.app.models.remediation import RemediationPlan, RemediationActionType, RiskLevel, ApprovalDecision
from backend.app.incidents.manager import incident_manager
from backend.app.rca.engine import rca_engine
from backend.app.monitoring.metric_buffer import metric_buffer
from backend.app.remediation.policy import policy_engine
from backend.app.remediation.executor import remediation_executor
from backend.app.core.security import get_current_user, require_permission, UserTokenData
from backend.app.core.logging import logger

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

class CreateIncidentRequest(BaseModel):
    service: str
    title: str
    severity: IncidentSeverity = IncidentSeverity.HIGH
    symptoms: List[str] = []

@router.get("", response_model=List[Dict[str, Any]])
def list_incidents(status: Optional[str] = None, current_user: UserTokenData = Depends(get_current_user)):
    all_incidents = [inc.model_dump() for inc in incident_manager.list_all_incidents()]
    if status:
        target = status.upper()
        if target == "WAITING_APPROVAL":
            return [i for i in all_incidents if i["status"] in ["WAITING_APPROVAL", "REMEDIATION_PROPOSED"]]
        return [i for i in all_incidents if i["status"] == target]
    return all_incidents

@router.post("", response_model=Dict[str, Any])
def create_incident(payload: CreateIncidentRequest, current_user: UserTokenData = Depends(get_current_user)):
    snapshot = metric_buffer.get_latest(payload.service)
    inc = incident_manager.create_incident(
        service=payload.service,
        title=payload.title,
        severity=payload.severity,
        symptoms=payload.symptoms,
        metrics=snapshot.model_dump() if snapshot else {}
    )
    return inc.model_dump()

@router.get("/{incident_id}", response_model=Dict[str, Any])
def get_incident(incident_id: str, current_user: UserTokenData = Depends(get_current_user)):
    inc = incident_manager.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return inc.model_dump()

@router.post("/{incident_id}/investigate")
def investigate_incident(incident_id: str, current_user: UserTokenData = Depends(require_permission("action:investigate"))):
    inc = incident_manager.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    snapshot = metric_buffer.get_latest(inc.service)
    logs = logger.search_logs(service=inc.service, limit=20)

    incident_manager.transition_state(
        incident_id,
        IncidentState.INVESTIGATING,
        actor=current_user.email,
        message=f"Investigation initiated by {current_user.email}. Retrieved telemetry and logs.",
        details={"logs_count": len(logs)}
    )

    inc.metrics = snapshot.model_dump() if snapshot else {}
    inc.logs = logs
    incident_manager.save_incident(inc)
    return {"message": "Investigation started", "incident": inc.model_dump()}

@router.post("/{incident_id}/diagnose")
def diagnose_incident(incident_id: str, current_user: UserTokenData = Depends(require_permission("action:diagnose"))):
    inc = incident_manager.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    snapshot = metric_buffer.get_latest(inc.service)
    if not snapshot:
        raise HTTPException(status_code=400, detail="No telemetry available to diagnose")

    logs = logger.search_logs(service=inc.service, limit=30)
    version = inc.metrics.get("version", "v1.0.0")

    rca_res = rca_engine.diagnose(snapshot, logs=logs, version=version)
    inc.rca = rca_res

    # Check if confidence meets threshold
    if rca_res.confidence < 0.50:
        incident_manager.transition_state(
            incident_id,
            IncidentState.NEEDS_HUMAN_REVIEW,
            actor="RCA_ENGINE",
            message=f"Root cause confidence ({rca_res.confidence:.2f}) below threshold. Escalated to human review."
        )
    else:
        incident_manager.transition_state(
            incident_id,
            IncidentState.DIAGNOSED,
            actor="RCA_ENGINE",
            message=f"Diagnosed root cause: {rca_res.root_cause.value} with {int(rca_res.confidence*100)}% confidence."
        )

        # Propose remediation plan via Policy Engine
        plan = policy_engine.select_remediation(inc)
        if plan:
            inc.recommended_action = plan.action.value
            inc.action_parameters = plan.parameters
            inc.risk_level = plan.risk_level.value
            inc.approval_required = (plan.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH])

            next_state = IncidentState.WAITING_APPROVAL if inc.approval_required else IncidentState.REMEDIATION_PROPOSED
            incident_manager.transition_state(
                incident_id,
                next_state,
                actor="POLICY_ENGINE",
                message=f"Proposed action: {plan.action.value} (Risk: {plan.risk_level.value})"
            )

    incident_manager.save_incident(inc)
    return {"message": "Diagnosis complete", "incident": inc.model_dump()}

@router.post("/{incident_id}/approve")
def approve_remediation(incident_id: str, current_user: UserTokenData = Depends(require_permission("remediation:approve:medium"))):
    inc = incident_manager.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    if inc.risk_level == RiskLevel.HIGH.value and "remediation:approve:high" not in current_user.permissions:
        raise HTTPException(status_code=403, detail="Approving HIGH risk actions requires ADMIN role")

    if not inc.recommended_action:
        raise HTTPException(status_code=400, detail="No recommended remediation action exists to approve")

    plan = RemediationPlan(
        action=RemediationActionType(inc.recommended_action),
        service=inc.service,
        parameters=inc.action_parameters,
        risk_level=RiskLevel(inc.risk_level or "MEDIUM"),
        reason=f"Approved by {current_user.email}",
        expected_outcome="Restores telemetry baseline"
    )

    # Execute remediation
    result = remediation_executor.execute_plan(
        plan=plan,
        actor=current_user.email,
        incident_id=incident_id,
        approved=True,
        approved_by=current_user.email
    )

    inc = incident_manager.get_incident(incident_id)
    return {"message": "Remediation executed", "result": result.model_dump(), "incident": inc.model_dump()}

@router.post("/{incident_id}/reject")
def reject_remediation(incident_id: str, reason: Optional[str] = None, current_user: UserTokenData = Depends(get_current_user)):
    inc = incident_manager.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident_manager.transition_state(
        incident_id,
        IncidentState.NEEDS_HUMAN_REVIEW,
        actor=current_user.email,
        message=f"Remediation plan rejected by {current_user.email}. Reason: {reason or 'Manual review requested'}"
    )
    return {"message": "Remediation rejected. Escalated to manual review.", "incident": inc.model_dump()}

@router.get("/{incident_id}/timeline")
def get_incident_timeline(incident_id: str, current_user: UserTokenData = Depends(get_current_user)):
    inc = incident_manager.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"incident_id": incident_id, "timeline": [t.model_dump() for t in inc.timeline]}
