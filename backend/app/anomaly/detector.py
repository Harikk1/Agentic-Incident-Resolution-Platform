from typing import Dict, Any, List, Optional
from backend.app.anomaly.thresholds import threshold_detector
from backend.app.anomaly.statistical import statistical_detector
from backend.app.anomaly.isolation_forest import ml_anomaly_detector
from backend.app.monitoring.metric_buffer import metric_buffer
from backend.app.models.metric import TelemetrySnapshot
from backend.app.models.incident import IncidentSeverity

class ComprehensiveAnomalyReport:
    def __init__(
        self,
        service: str,
        is_anomalous: bool,
        severity: IncidentSeverity,
        threshold_violations: List[Dict[str, Any]],
        statistical_anomalies: List[Dict[str, Any]],
        ml_anomaly: Dict[str, Any],
        summary: str
    ):
        self.service = service
        self.is_anomalous = is_anomalous
        self.severity = severity
        self.threshold_violations = threshold_violations
        self.statistical_anomalies = statistical_anomalies
        self.ml_anomaly = ml_anomaly
        self.summary = summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "is_anomalous": self.is_anomalous,
            "severity": self.severity.value,
            "threshold_violations": self.threshold_violations,
            "statistical_anomalies": self.statistical_anomalies,
            "ml_anomaly": self.ml_anomaly,
            "summary": self.summary
        }

class HybridAnomalyDetector:
    def analyze_service(self, service_name: str, snapshot: Optional[TelemetrySnapshot] = None) -> ComprehensiveAnomalyReport:
        if snapshot is None:
            snapshot = metric_buffer.get_latest(service_name)
            if snapshot is None:
                snapshot = TelemetrySnapshot(service=service_name)

        history = metric_buffer.get_history(service_name, count=30)

        # 1. Threshold Detection (Deterministic)
        threshold_violations = [v.to_dict() for v in threshold_detector.evaluate(snapshot)]

        # 2. Statistical Detection
        stat_anomalies = statistical_detector.analyze_snapshot(snapshot, history)

        # 3. ML Detection (Isolation Forest)
        ml_res = ml_anomaly_detector.detect(snapshot, history).to_dict()

        # Determine overall severity
        has_critical = any(v.get("severity") == IncidentSeverity.CRITICAL.value for v in threshold_violations)
        has_high = any(v.get("severity") == IncidentSeverity.HIGH.value for v in threshold_violations)

        is_anomalous = False
        severity = IncidentSeverity.NORMAL

        if has_critical:
            is_anomalous = True
            severity = IncidentSeverity.CRITICAL
        elif has_high or ml_res["is_anomaly"] or len(stat_anomalies) >= 2:
            is_anomalous = True
            severity = IncidentSeverity.HIGH
        elif len(stat_anomalies) > 0 or len(threshold_violations) > 0:
            is_anomalous = True
            severity = IncidentSeverity.HIGH

        # Construct concise summary
        reasons = []
        if threshold_violations:
            reasons.append(f"{len(threshold_violations)} threshold violation(s)")
        if stat_anomalies:
            reasons.append(f"{len(stat_anomalies)} statistical deviation(s)")
        if ml_res["is_anomaly"]:
            reasons.append(f"multivariate isolation anomaly (features: {', '.join(ml_res['affected_features'])})")

        summary = f"{service_name}: " + ("; ".join(reasons) if reasons else "telemetry within normal boundaries")

        return ComprehensiveAnomalyReport(
            service=service_name,
            is_anomalous=is_anomalous,
            severity=severity,
            threshold_violations=threshold_violations,
            statistical_anomalies=stat_anomalies,
            ml_anomaly=ml_res,
            summary=summary
        )

hybrid_detector = HybridAnomalyDetector()
