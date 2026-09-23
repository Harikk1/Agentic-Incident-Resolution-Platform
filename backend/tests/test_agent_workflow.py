import pytest
from agent.agent import smartops_agent
from backend.app.models.metric import TelemetrySnapshot
from backend.app.monitoring.metric_buffer import metric_buffer

def test_agent_investigation_workflow():
    # Inject traffic surge telemetry into metric buffer
    metric_buffer.add_snapshot(
        "payment-service",
        TelemetrySnapshot(
            service="payment-service",
            request_rate=720.0,
            cpu_percent=89.0,
            latency_ms=185.0
        )
    )

    state = smartops_agent.process_message(
        user_message="Payment service is slow. Find the cause and fix it.",
        session_id="ses-test-99",
        approved=False
    )

    assert state.service == "payment-service"
    assert state.rca_result is not None
    assert state.rca_result.get("root_cause") == "TRAFFIC_SPIKE"
    assert state.recommended_action == "scale_service"
    assert state.approval_status == "PENDING"
    assert len(state.tool_traces) >= 5
    assert "scale_service" in state.final_response

def test_agent_approval_and_execution_workflow():
    state = smartops_agent.process_message(
        user_message="Approve remediation for payment-service",
        session_id="ses-test-99",
        approved=True,
        action_override="scale_service"
    )

    assert state.approval_status == "APPROVED"
    assert state.execution_result is not None
    assert state.execution_result.get("status") == "SUCCESS"
    assert state.verification_result is not None
