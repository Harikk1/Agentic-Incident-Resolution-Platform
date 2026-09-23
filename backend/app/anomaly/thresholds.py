from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.models.metric import TelemetrySnapshot
from backend.app.models.incident import IncidentSeverity

class ThresholdViolation:
    def __init__(self, metric_name: str, value: float, threshold: float, severity: IncidentSeverity, message: str):
        self.metric_name = metric_name
        self.value = value
        self.threshold = threshold
        self.severity = severity
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric_name,
            "value": self.value,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "message": self.message
        }

class ThresholdDetector:
    def evaluate(self, snapshot: TelemetrySnapshot) -> List[ThresholdViolation]:
        violations: List[ThresholdViolation] = []

        # 1. CPU Evaluation
        if snapshot.cpu_percent >= settings.CPU_THRESHOLD_CRITICAL:
            violations.append(ThresholdViolation(
                "cpu_percent", snapshot.cpu_percent, settings.CPU_THRESHOLD_CRITICAL, IncidentSeverity.CRITICAL,
                f"CPU utilization at {snapshot.cpu_percent:.1f}% exceeds critical threshold ({settings.CPU_THRESHOLD_CRITICAL}%)"
            ))
        elif snapshot.cpu_percent >= settings.CPU_THRESHOLD_HIGH:
            violations.append(ThresholdViolation(
                "cpu_percent", snapshot.cpu_percent, settings.CPU_THRESHOLD_HIGH, IncidentSeverity.HIGH,
                f"CPU utilization at {snapshot.cpu_percent:.1f}% exceeds high threshold ({settings.CPU_THRESHOLD_HIGH}%)"
            ))

        # 2. Memory Evaluation
        if snapshot.memory_percent >= settings.MEMORY_THRESHOLD_CRITICAL:
            violations.append(ThresholdViolation(
                "memory_percent", snapshot.memory_percent, settings.MEMORY_THRESHOLD_CRITICAL, IncidentSeverity.CRITICAL,
                f"Memory usage at {snapshot.memory_percent:.1f}% exceeds critical threshold ({settings.MEMORY_THRESHOLD_CRITICAL}%)"
            ))
        elif snapshot.memory_percent >= settings.MEMORY_THRESHOLD_HIGH:
            violations.append(ThresholdViolation(
                "memory_percent", snapshot.memory_percent, settings.MEMORY_THRESHOLD_HIGH, IncidentSeverity.HIGH,
                f"Memory usage at {snapshot.memory_percent:.1f}% exceeds high threshold ({settings.MEMORY_THRESHOLD_HIGH}%)"
            ))

        # 3. Disk Evaluation
        if snapshot.disk_percent >= settings.DISK_THRESHOLD_CRITICAL:
            violations.append(ThresholdViolation(
                "disk_percent", snapshot.disk_percent, settings.DISK_THRESHOLD_CRITICAL, IncidentSeverity.CRITICAL,
                f"Disk usage at {snapshot.disk_percent:.1f}% exceeds critical threshold ({settings.DISK_THRESHOLD_CRITICAL}%)"
            ))
        elif snapshot.disk_percent >= settings.DISK_THRESHOLD_HIGH:
            violations.append(ThresholdViolation(
                "disk_percent", snapshot.disk_percent, settings.DISK_THRESHOLD_HIGH, IncidentSeverity.HIGH,
                f"Disk usage at {snapshot.disk_percent:.1f}% exceeds high threshold ({settings.DISK_THRESHOLD_HIGH}%)"
            ))

        # 4. Latency Evaluation
        if snapshot.latency_ms >= settings.LATENCY_THRESHOLD_CRITICAL_MS:
            violations.append(ThresholdViolation(
                "latency_ms", snapshot.latency_ms, settings.LATENCY_THRESHOLD_CRITICAL_MS, IncidentSeverity.CRITICAL,
                f"Response latency at {snapshot.latency_ms:.1f}ms exceeds critical threshold ({settings.LATENCY_THRESHOLD_CRITICAL_MS}ms)"
            ))
        elif snapshot.latency_ms >= settings.LATENCY_THRESHOLD_HIGH_MS:
            violations.append(ThresholdViolation(
                "latency_ms", snapshot.latency_ms, settings.LATENCY_THRESHOLD_HIGH_MS, IncidentSeverity.HIGH,
                f"Response latency at {snapshot.latency_ms:.1f}ms exceeds high threshold ({settings.LATENCY_THRESHOLD_HIGH_MS}ms)"
            ))

        # 5. Error Rate Evaluation
        if snapshot.error_rate >= settings.ERROR_RATE_THRESHOLD_CRITICAL:
            violations.append(ThresholdViolation(
                "error_rate", snapshot.error_rate, settings.ERROR_RATE_THRESHOLD_CRITICAL, IncidentSeverity.CRITICAL,
                f"Error rate at {snapshot.error_rate*100:.1f}% exceeds critical threshold ({settings.ERROR_RATE_THRESHOLD_CRITICAL*100}%)"
            ))
        elif snapshot.error_rate >= settings.ERROR_RATE_THRESHOLD_HIGH:
            violations.append(ThresholdViolation(
                "error_rate", snapshot.error_rate, settings.ERROR_RATE_THRESHOLD_HIGH, IncidentSeverity.HIGH,
                f"Error rate at {snapshot.error_rate*100:.1f}% exceeds high threshold ({settings.ERROR_RATE_THRESHOLD_HIGH*100}%)"
            ))

        # 6. Service Availability (Crash)
        if snapshot.pod_availability < 0.5:
            violations.append(ThresholdViolation(
                "pod_availability", snapshot.pod_availability, 0.5, IncidentSeverity.CRITICAL,
                "Service endpoint is completely unresponsive / Pod down"
            ))

        return violations

threshold_detector = ThresholdDetector()
