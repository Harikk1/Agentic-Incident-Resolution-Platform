import pytest
from backend.app.models.metric import TelemetrySnapshot
from backend.app.monitoring.collector import collector
from backend.app.incidents.manager import incident_manager
from backend.app.models.incident import IncidentState

@pytest.mark.asyncio
async def test_mode_a_auto_incident_and_approval_queue():
    service = "payment-service"
    # Resolve any existing active incident for isolation
    old_inc = incident_manager.get_active_incident_for_service(service)
    if old_inc:
        old_inc.status = IncidentState.RESOLVED
        incident_manager.save_incident(old_inc)

    # 1. Simulate anomalous telemetry snapshot (Traffic surge + high CPU)
    snapshot = TelemetrySnapshot(
        service=service,
        request_rate=850.0,
        cpu_percent=94.0,
        latency_ms=210.0,
        database_latency_ms=20.0
    )

    # 2. Trigger Mode A evaluation
    service_info = {"name": service, "version": "v1.0.0"}
    await collector.evaluate_mode_a(service, snapshot, service_info)

    # 3. Verify that incident was automatically created and reached WAITING_APPROVAL
    active_inc = incident_manager.get_active_incident_for_service(service)
    assert active_inc is not None, "Auto-incident should have been created"
    assert active_inc.status == IncidentState.WAITING_APPROVAL, f"Expected WAITING_APPROVAL, got {active_inc.status}"
    assert active_inc.recommended_action == "scale_service"
    assert active_inc.approval_required is True

    # 4. Verify that approval queue query returns this incident
    all_waiting = [i for i in incident_manager.list_all_incidents() if i.status == IncidentState.WAITING_APPROVAL]
    assert any(i.incident_id == active_inc.incident_id for i in all_waiting)
