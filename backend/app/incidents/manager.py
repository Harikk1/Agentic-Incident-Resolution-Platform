import time
import uuid
from typing import List, Optional, Dict, Any
from backend.app.models.incident import Incident, IncidentState, IncidentSeverity, RCAResult, IncidentTimelineEvent
from backend.app.models.metric import TelemetrySnapshot
from backend.app.incidents.lifecycle import lifecycle
from backend.app.database.repositories import incidents_repo
from backend.app.core.logging import logger

class IncidentManager:
    def create_incident(
        self,
        service: str,
        title: str,
        severity: IncidentSeverity = IncidentSeverity.HIGH,
        symptoms: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        logs: Optional[List[Dict[str, Any]]] = None
    ) -> Incident:
        # Check if an active unresolved incident already exists for this service
        active = self.get_active_incident_for_service(service)
        if active:
            return active

        incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
        now = time.time()
        incident = Incident(
            incident_id=incident_id,
            service=service,
            severity=severity,
            status=IncidentState.DETECTED,
            title=title,
            symptoms=symptoms or [],
            metrics=metrics or {},
            logs=logs or [],
            created_at=now,
            updated_at=now
        )
        
        incident.timeline.append(IncidentTimelineEvent(
            timestamp=now,
            from_state=None,
            to_state=IncidentState.DETECTED.value,
            actor="SYSTEM",
            message="Anomaly detected. Incident created."
        ))
        self.save_incident(incident)
        return incident

    def save_incident(self, incident: Incident) -> Incident:
        data = incident.model_dump()
        incidents_repo.save(data)
        return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        data = incidents_repo.get_by_id(incident_id)
        if data:
            return Incident(**data)
        return None

    def get_active_incidents(self) -> List[Incident]:
        all_incidents = [Incident(**d) for d in incidents_repo.list_all()]
        return [inc for inc in all_incidents if inc.status != IncidentState.RESOLVED]

    def get_active_incident_for_service(self, service: str) -> Optional[Incident]:
        active = self.get_active_incidents()
        for inc in active:
            if inc.service == service:
                return inc
        return None

    def list_all_incidents(self) -> List[Incident]:
        return [Incident(**d) for d in incidents_repo.list_all()]

    def transition_state(
        self,
        incident_id: str,
        target_state: IncidentState,
        actor: str = "SYSTEM",
        message: str = "",
        details: Optional[Dict[str, Any]] = None
    ) -> Incident:
        incident = self.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        updated = lifecycle.transition(incident, target_state, actor=actor, message=message, details=details)
        self.save_incident(updated)
        return updated

incident_manager = IncidentManager()
