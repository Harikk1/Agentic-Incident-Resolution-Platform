import pytest
from backend.app.models.incident import IncidentState
from backend.app.incidents.state_machine import validate_transition, InvalidStateTransitionError
from backend.app.incidents.manager import incident_manager

def test_valid_state_transitions():
    assert validate_transition(IncidentState.DETECTED, IncidentState.INVESTIGATING) is True
    assert validate_transition(IncidentState.INVESTIGATING, IncidentState.DIAGNOSED) is True
    assert validate_transition(IncidentState.DIAGNOSED, IncidentState.REMEDIATION_PROPOSED) is True
    assert validate_transition(IncidentState.REMEDIATION_PROPOSED, IncidentState.WAITING_APPROVAL) is True
    assert validate_transition(IncidentState.WAITING_APPROVAL, IncidentState.REMEDIATION_EXECUTING) is True
    assert validate_transition(IncidentState.REMEDIATION_EXECUTING, IncidentState.VERIFYING) is True
    assert validate_transition(IncidentState.VERIFYING, IncidentState.RESOLVED) is True

def test_invalid_state_transition_raises():
    with pytest.raises(InvalidStateTransitionError):
        # Cannot jump from DETECTED directly to RESOLVED without verification or transition
        validate_transition(IncidentState.DETECTED, IncidentState.REMEDIATION_EXECUTING)

def test_incident_manager_creation():
    inc = incident_manager.create_incident(
        service="new-test-service",
        title="Payment Latency Anomaly",
        symptoms=["Latency > 200ms"]
    )
    assert inc.incident_id.startswith("INC-")
    assert inc.status == IncidentState.DETECTED
    assert len(inc.timeline) >= 1
