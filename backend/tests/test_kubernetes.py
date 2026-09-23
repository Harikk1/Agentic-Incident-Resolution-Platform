import pytest
from backend.app.kubernetes.mock_driver import MockKubernetesDriver

def test_mock_k8s_scale_and_status():
    driver = MockKubernetesDriver()
    res = driver.scale_deployment("payment-service", 5)
    assert res["status"] == "SUCCESS"
    assert res["desired_replicas"] == 5

    status = driver.get_deployment_status("payment-service")
    assert status["desired_replicas"] == 5
    assert status["ready_replicas"] == 5

    pods = driver.get_pods("payment-service")
    assert len(pods) == 5

def test_mock_k8s_restart():
    driver = MockKubernetesDriver()
    res = driver.restart_deployment("payment-service")
    assert res["status"] == "SUCCESS"
    pods = driver.get_pods("payment-service")
    assert any(p["restart_count"] >= 1 for p in pods)

def test_mock_k8s_rollback():
    driver = MockKubernetesDriver()
    res = driver.rollback_deployment("payment-service")
    assert res["status"] == "SUCCESS"
    status = driver.get_deployment_status("payment-service")
    assert status["version"] == "v1.0.0"
