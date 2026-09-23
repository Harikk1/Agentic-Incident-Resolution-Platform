# Testing Strategy & Verification Report

SmartOps features a comprehensive test suite across unit, integration, security, and end-to-end incident workflows.

## Test Suite Summary (35 Tests Passing)

### Unit Tests
- `test_metrics.py`: Metric buffer capacity, sliding window eviction, and telemetry serialization.
- `test_thresholds.py`: Layer 1 deterministic threshold detector across normal, high, and critical levels.
- `test_anomaly.py`: Layer 2 Z-score/IQR statistical detection and Layer 3 multivariate Isolation Forest outlier detection.
- `test_rca.py`: Root Cause Analysis engine across Traffic Spike, Database Bottleneck, Memory Leak, Bad Deployment, and fallback to `UNKNOWN`.
- `test_incident.py`: Incident lifecycle state machine transitions and invalid transition rejections.
- `test_remediation_policy.py`: Mode A deterministic policy selection logic.
- `test_kubernetes.py`: Mock Kubernetes driver scaling, rollout restart, rollback, and resource patching.
- `test_mcp_tools.py`: FastMCP tools execution and structured execution trace capture.
- `test_approval.py`: Risk classification and human approval gating.

### Security Tests
- `test_security_rbac.py`: RBAC permission matrix enforcement, viewer restrictions, invalid service rejection, and replica count validation.

### Integration & End-to-End Tests
- `test_agent_workflow.py`: Agent state machine progression from request understanding through MCP tool calling, RCA, and verified remediation.
- `test_e2e_remediation.py`: Full Detect $\to$ Investigate $\to$ Diagnose $\to$ Plan $\to$ Approve $\to$ Execute $\to$ Verify $\to$ Audit lifecycle.

## Running Tests Locally
```bash
.venv\Scripts\pytest -v backend/tests
```
