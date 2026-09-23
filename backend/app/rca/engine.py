from typing import List, Dict, Any, Optional
from backend.app.rca.evidence import TelemetryEvidence
from backend.app.rca.rules import RCARuleEvaluator
from backend.app.models.incident import RootCause, RCAResult
from backend.app.models.metric import TelemetrySnapshot

class RCAEngine:
    def diagnose(
        self,
        snapshot: TelemetrySnapshot,
        logs: Optional[List[Dict[str, Any]]] = None,
        dependencies: Optional[List[Dict[str, Any]]] = None,
        version: str = "v1.0.0"
    ) -> RCAResult:
        evidence = TelemetryEvidence.extract_evidence(snapshot, logs, dependencies, version)

        candidates = [
            (RootCause.TRAFFIC_SPIKE, RCARuleEvaluator.evaluate_traffic_spike(evidence)),
            (RootCause.DATABASE_BOTTLENECK, RCARuleEvaluator.evaluate_database_bottleneck(evidence)),
            (RootCause.BAD_DEPLOYMENT, RCARuleEvaluator.evaluate_bad_deployment(evidence, version)),
            (RootCause.MEMORY_LEAK, RCARuleEvaluator.evaluate_memory_leak(evidence)),
            (RootCause.SERVICE_FAILURE, RCARuleEvaluator.evaluate_service_failure(evidence)),
            (RootCause.DEPENDENCY_FAILURE, RCARuleEvaluator.evaluate_dependency_failure(evidence)),
            (RootCause.CPU_SATURATION, RCARuleEvaluator.evaluate_cpu_saturation(evidence)),
            (RootCause.DISK_PRESSURE, RCARuleEvaluator.evaluate_disk_pressure(evidence)),
        ]

        # Sort by confidence score descending
        candidates.sort(key=lambda x: x[1][0], reverse=True)

        top_cause, (top_score, top_evidence) = candidates[0]

        # Require minimum confidence threshold of 0.50
        if top_score < 0.50:
            return RCAResult(
                root_cause=RootCause.UNKNOWN,
                confidence=round(top_score, 2),
                evidence=evidence["facts"] or ["Insufficient telemetry correlation to establish definitive root cause."],
                contributing_factors=["Telemetry levels within ambiguous variance boundaries."]
            )

        # Gather secondary contributing factors from other high-scoring causes
        contributing = []
        for cause, (score, reasons) in candidates[1:]:
            if score >= 0.40:
                contributing.append(f"{cause.value} ({int(score*100)}%): " + "; ".join(reasons))

        return RCAResult(
            root_cause=top_cause,
            confidence=round(top_score, 2),
            evidence=top_evidence,
            contributing_factors=contributing
        )

rca_engine = RCAEngine()
