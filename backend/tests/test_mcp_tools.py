import pytest
from agent.mcp_client import mcp_client

def test_mcp_monitoring_tools():
    # 1. get_all_services
    res_all = mcp_client.call_tool("get_all_services", {})
    assert res_all["trace"].status == "COMPLETED"
    assert len(res_all["result"]) >= 3

    # 2. get_service_metrics
    res_m = mcp_client.call_tool("get_service_metrics", {"service": "payment-service"})
    assert res_m["trace"].status == "COMPLETED"

    # 3. get_service_health
    res_h = mcp_client.call_tool("get_service_health", {"service": "user-service"})
    assert res_h["trace"].status == "COMPLETED"

def test_mcp_diagnostic_tools():
    res_ano = mcp_client.call_tool("detect_anomaly", {"service": "payment-service"})
    assert res_ano["trace"].status == "COMPLETED"
    assert "is_anomalous" in res_ano["result"]

    res_rca = mcp_client.call_tool("predict_root_cause", {"service": "payment-service"})
    assert res_rca["trace"].status == "COMPLETED"
    assert "root_cause" in res_rca["result"]

def test_mcp_remediation_tool():
    res_scale = mcp_client.call_tool("scale_service", {"service": "payment-service", "replicas": 4, "approved": True})
    assert res_scale["trace"].status == "COMPLETED"
    assert res_scale["result"]["status"] == "SUCCESS"
