import pytest
from backend.app.models.metric import TelemetrySnapshot
from backend.app.monitoring.metric_buffer import metric_buffer
from backend.app.incidents.manager import incident_manager
from backend.app.rca.engine import rca_engine
from backend.app.remediation.policy import policy_engine
from backend.app.remediation.executor import remediation_executor
from backend.app.models.incident import IncidentState, RootCause
from backend.app.database.repositories import audit_repo

def test_full_end_to_end_incident_flow():
    service = "payment-service"
    # Resolve any existing active incident for isolation
    old_inc = incident_manager.get_active_incident_for_service(service)
    if old_inc:
        old_inc.status = IncidentState.RESOLVED
        incident_manager.save_incident(old_inc)

    # 1. Telemetry surge triggers incident creation
    snapshot = TelemetrySnapshot(
        service=service,
        request_rate=800.0,
        cpu_percent=92.0,
        latency_ms=195.0,
        database_latency_ms=20.0
    )
    metric_buffer.add_snapshot(service, snapshot)

    incident = incident_manager.create_incident(
        service=service,
        title="High Traffic Anomaly on Payment Gateway",
        symptoms=["Request rate > 800 req/s", "CPU > 90%"]
    )
    assert incident.status == IncidentState.DETECTED

    # 2. Investigation step
    incident_manager.transition_state(incident.incident_id, IncidentState.INVESTIGATING, actor="SYSTEM")
    incident = incident_manager.get_incident(incident.incident_id)
    assert incident.status == IncidentState.INVESTIGATING

    # 3. RCA Diagnosis
    rca = rca_engine.diagnose(snapshot)
    incident.rca = rca
    assert rca.root_cause == RootCause.TRAFFIC_SPIKE
    assert rca.confidence >= 0.85

    incident_manager.transition_state(incident.incident_id, IncidentState.DIAGNOSED, actor="RCA_ENGINE")

    # 4. Remediation Planning via Policy Engine
    plan = policy_engine.select_remediation(incident)
    assert plan is not None
    assert plan.action.value == "scale_service"

    incident_manager.transition_state(
        incident.incident_id,
        IncidentState.WAITING_APPROVAL,
        actor="POLICY_ENGINE",
        message=f"Action {plan.action.value} requires approval"
    )

    # 5. Human Approval & Execution
    result = remediation_executor.execute_plan(
        plan=plan,
        actor="lead-sre@smartops.ai",
        incident_id=incident.incident_id,
        approved=True,
        approved_by="lead-sre@smartops.ai"
    )

    assert result.status == "SUCCESS"
    assert result.health_verified is True

    # 6. Incident Resolved & Verified
    resolved_incident = incident_manager.get_incident(incident.incident_id)
    assert resolved_incident.status == IncidentState.RESOLVED
    assert resolved_incident.resolved_at is not None

    # 7. Audit Record Verified
    audits = audit_repo.list_all()
    matching_audit = [a for a in audits if a["action_id"] == result.action_id]
    assert len(matching_audit) == 1
    assert matching_audit[0]["result"] == "SUCCESS"
    assert matching_audit[0]["approved"] is True
