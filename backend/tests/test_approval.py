import pytest
from backend.app.models.remediation import RemediationPlan, RemediationActionType, RiskLevel
from backend.app.remediation.executor import remediation_executor
from backend.app.database.repositories import audit_repo

def test_high_risk_unapproved_remediation_rejected():
    plan = RemediationPlan(
        action=RemediationActionType.ROLLBACK_DEPLOYMENT,
        service="payment-service",
        parameters={},
        risk_level=RiskLevel.HIGH,
        reason="Test rollback",
        expected_outcome="Restore stable release"
    )
    with pytest.raises(PermissionError):
        remediation_executor.execute_plan(plan, actor="engineer@smartops.ai", approved=False)

def test_high_risk_approved_remediation_succeeds_and_audited():
    plan = RemediationPlan(
        action=RemediationActionType.ROLLBACK_DEPLOYMENT,
        service="payment-service",
        parameters={},
        risk_level=RiskLevel.HIGH,
        reason="Test rollback",
        expected_outcome="Restore stable release"
    )
    res = remediation_executor.execute_plan(plan, actor="admin@smartops.ai", approved=True, approved_by="admin@smartops.ai")
    assert res.status == "SUCCESS"

    # Verify audit trail record was generated
    recent_audits = audit_repo.list_all()
    matching = [a for a in recent_audits if a["action_id"] == res.action_id]
    assert len(matching) == 1
    assert matching[0]["risk"] == "HIGH"
    assert matching[0]["approved"] is True
