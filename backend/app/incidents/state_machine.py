from typing import Dict, Set
from backend.app.models.incident import IncidentState

# Explicit state transition graph
VALID_TRANSITIONS: Dict[IncidentState, Set[IncidentState]] = {
    IncidentState.DETECTED: {
        IncidentState.INVESTIGATING,
        IncidentState.RESOLVED  # Transient spike auto-recovery
    },
    IncidentState.INVESTIGATING: {
        IncidentState.DIAGNOSED,
        IncidentState.NEEDS_HUMAN_REVIEW,
        IncidentState.RESOLVED
    },
    IncidentState.DIAGNOSED: {
        IncidentState.REMEDIATION_PROPOSED,
        IncidentState.WAITING_APPROVAL,
        IncidentState.NEEDS_HUMAN_REVIEW,
        IncidentState.RESOLVED
    },
    IncidentState.REMEDIATION_PROPOSED: {
        IncidentState.WAITING_APPROVAL,
        IncidentState.REMEDIATION_EXECUTING,  # Low-risk auto-approved
        IncidentState.NEEDS_HUMAN_REVIEW,
        IncidentState.RESOLVED
    },
    IncidentState.WAITING_APPROVAL: {
        IncidentState.REMEDIATION_EXECUTING,  # Approved
        IncidentState.NEEDS_HUMAN_REVIEW,    # Rejected or Escalate
        IncidentState.RESOLVED
    },
    IncidentState.REMEDIATION_EXECUTING: {
        IncidentState.VERIFYING,
        IncidentState.REMEDIATION_FAILED
    },
    IncidentState.VERIFYING: {
        IncidentState.RESOLVED,
        IncidentState.REMEDIATION_FAILED,
        IncidentState.NEEDS_HUMAN_REVIEW
    },
    IncidentState.REMEDIATION_FAILED: {
        IncidentState.NEEDS_HUMAN_REVIEW,
        IncidentState.INVESTIGATING,
        IncidentState.RESOLVED
    },
    IncidentState.NEEDS_HUMAN_REVIEW: {
        IncidentState.INVESTIGATING,
        IncidentState.REMEDIATION_PROPOSED,
        IncidentState.RESOLVED
    },
    IncidentState.RESOLVED: {
        IncidentState.DETECTED  # Reopened on subsequent recurring failure
    }
}

class InvalidStateTransitionError(Exception):
    def __init__(self, current_state: IncidentState, target_state: IncidentState):
        super().__init__(f"Invalid transition from state '{current_state.value}' to '{target_state.value}'")
        self.current_state = current_state
        self.target_state = target_state

def validate_transition(current: IncidentState, target: IncidentState) -> bool:
    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionError(current, target)
    return True
