import time
from typing import Dict, Any, Optional
from backend.app.models.incident import Incident, IncidentState, IncidentTimelineEvent
from backend.app.incidents.state_machine import validate_transition
from backend.app.core.logging import logger

class IncidentLifecycle:
    @staticmethod
    def transition(
        incident: Incident,
        target_state: IncidentState,
        actor: str = "SYSTEM",
        message: str = "",
        details: Optional[Dict[str, Any]] = None
    ) -> Incident:
        old_state = incident.status
        validate_transition(old_state, target_state)

        incident.status = target_state
        incident.updated_at = time.time()

        if target_state == IncidentState.RESOLVED:
            incident.resolved_at = time.time()

        event = IncidentTimelineEvent(
            timestamp=time.time(),
            from_state=old_state.value,
            to_state=target_state.value,
            actor=actor,
            message=message or f"Transitioned from {old_state.value} to {target_state.value}",
            details=details or {}
        )
        incident.timeline.append(event)

        logger.info(
            f"Incident {incident.incident_id} state changed: {old_state.value} -> {target_state.value}",
            incident_id=incident.incident_id,
            service=incident.service,
            extra={"actor": actor, "message": message}
        )

        return incident

lifecycle = IncidentLifecycle()
