import pytest
from backend.app.models.incident import Incident, RootCause, RCAResult, IncidentSeverity
from backend.app.remediation.policy import policy_engine
from backend.app.models.remediation import RemediationActionType

def test_policy_traffic_spike_scales_service():
    inc = Incident(
        incident_id="INC-TEST-01",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
        title="Traffic Spike Incident",
        rca=RCAResult(root_cause=RootCause.TRAFFIC_SPIKE, confidence=0.92)
    )
    plan = policy_engine.select_remediation(inc)
    assert plan is not None
    assert plan.action == RemediationActionType.SCALE_SERVICE
    assert plan.parameters.get("replicas") > 2

def test_policy_bad_deployment_rolls_back():
    inc = Incident(
        incident_id="INC-TEST-02",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
        title="Bad Deployment Incident",
        rca=RCAResult(root_cause=RootCause.BAD_DEPLOYMENT, confidence=0.88)
    )
    plan = policy_engine.select_remediation(inc)
    assert plan is not None
    assert plan.action == RemediationActionType.ROLLBACK_DEPLOYMENT

def test_policy_database_bottleneck_does_not_scale():
    inc = Incident(
        incident_id="INC-TEST-03",
        service="payment-service",
        severity=IncidentSeverity.HIGH,
        title="DB Bottleneck",
        rca=RCAResult(root_cause=RootCause.DATABASE_BOTTLENECK, confidence=0.90)
    )
    # Critical: Policy engine must NOT blindly scale payment pods
    plan = policy_engine.select_remediation(inc)
    assert plan is None
