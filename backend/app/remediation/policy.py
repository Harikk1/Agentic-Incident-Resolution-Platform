from typing import Optional, Dict, Any
from backend.app.models.incident import RootCause, RCAResult, Incident
from backend.app.models.remediation import RemediationPlan, RemediationActionType, RiskLevel

class DeterministicRemediationPolicyEngine:
    """Mode A: Deterministic Policy Engine for Automated AIOps"""

    def select_remediation(self, incident: Incident) -> Optional[RemediationPlan]:
        if not incident.rca or incident.rca.root_cause == RootCause.UNKNOWN:
            return None

        cause = incident.rca.root_cause
        service = incident.service
        curr_replicas = incident.metrics.get("desired_replicas", 2)

        if cause == RootCause.TRAFFIC_SPIKE:
            target_replicas = min(curr_replicas + 3, 8)
            return RemediationPlan(
                action=RemediationActionType.SCALE_SERVICE,
                service=service,
                parameters={"replicas": target_replicas},
                risk_level=RiskLevel.MEDIUM,
                reason="Traffic surge detected exceeding cluster capacity thresholds",
                expected_outcome=f"Distribute incoming load across {target_replicas} pods, dropping latency below 70ms"
            )

        elif cause == RootCause.CPU_SATURATION:
            target_replicas = min(curr_replicas + 2, 6)
            return RemediationPlan(
                action=RemediationActionType.SCALE_SERVICE,
                service=service,
                parameters={"replicas": target_replicas},
                risk_level=RiskLevel.MEDIUM,
                reason="CPU utilization saturation requires horizontal replica expansion",
                expected_outcome="Reduce per-pod CPU load to nominal baseline"
            )

        elif cause == RootCause.MEMORY_LEAK:
            return RemediationPlan(
                action=RemediationActionType.RESTART_SERVICE,
                service=service,
                parameters={},
                risk_level=RiskLevel.MEDIUM,
                reason="Memory ceiling reached with growing leak signature",
                expected_outcome="Rollout restart clears leaked heap buffers and stabilizes memory"
            )

        elif cause == RootCause.SERVICE_FAILURE:
            return RemediationPlan(
                action=RemediationActionType.RESTART_POD,
                service=service,
                parameters={},
                risk_level=RiskLevel.MEDIUM,
                reason="Unresponsive or crashed container requires pod recreation",
                expected_outcome="Restore service availability and healthy health endpoint checks"
            )

        elif cause == RootCause.BAD_DEPLOYMENT:
            return RemediationPlan(
                action=RemediationActionType.ROLLBACK_DEPLOYMENT,
                service=service,
                parameters={},
                risk_level=RiskLevel.HIGH,
                reason="High error rate immediately following regression build release",
                expected_outcome="Restore previous known-good deployment revision v1.0.0"
            )

        elif cause == RootCause.DISK_PRESSURE:
            return RemediationPlan(
                action=RemediationActionType.CLEANUP_DISK,
                service=service,
                parameters={},
                risk_level=RiskLevel.LOW,
                reason="Storage capacity threshold exceeded",
                expected_outcome="Free volume capacity by clearing stale logs and temp files"
            )

        elif cause == RootCause.DATABASE_BOTTLENECK:
            # Crucial: Do NOT scale application when DB is the bottleneck!
            return None

        return None

policy_engine = DeterministicRemediationPolicyEngine()
