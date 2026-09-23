import pytest
from backend.app.core.security import ROLE_PERMISSIONS, Role
from backend.app.remediation.actions import remediation_actions

def test_viewer_role_has_no_remediation_permissions():
    perms = ROLE_PERMISSIONS[Role.VIEWER]
    assert "read:services" in perms
    assert "remediation:approve:medium" not in perms
    assert "remediation:approve:high" not in perms
    assert "remediation:execute:all" not in perms

def test_engineer_cannot_approve_high_risk():
    perms = ROLE_PERMISSIONS[Role.ENGINEER]
    assert "remediation:approve:medium" in perms
    assert "remediation:approve:high" not in perms

def test_admin_has_all_permissions():
    perms = ROLE_PERMISSIONS[Role.ADMIN]
    assert "remediation:approve:high" in perms
    assert "remediation:execute:all" in perms

def test_invalid_service_rejected():
    with pytest.raises(ValueError, match="not in allowed services"):
        remediation_actions.scale_service("malicious-injected-svc", 3)

def test_invalid_replica_count_rejected():
    with pytest.raises(ValueError, match="Replica count"):
        remediation_actions.scale_service("payment-service", 999)

    with pytest.raises(ValueError, match="Replica count"):
        remediation_actions.scale_service("payment-service", 0)
