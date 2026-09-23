import pytest
from backend.app.models.metric import TelemetrySnapshot
from backend.app.anomaly.thresholds import threshold_detector
from backend.app.models.incident import IncidentSeverity

def test_threshold_detector_normal():
    snap = TelemetrySnapshot(
        service="user-service",
        cpu_percent=30.0,
        memory_percent=40.0,
        disk_percent=50.0,
        latency_ms=25.0,
        error_rate=0.001
    )
    violations = threshold_detector.evaluate(snap)
    assert len(violations) == 0

def test_threshold_detector_high_and_critical():
    # High CPU (75%) and Critical Latency (160ms)
    snap = TelemetrySnapshot(
        service="payment-service",
        cpu_percent=75.0,
        latency_ms=160.0
    )
    violations = threshold_detector.evaluate(snap)
    assert len(violations) == 2

    cpu_v = next(v for v in violations if v.metric_name == "cpu_percent")
    assert cpu_v.severity == IncidentSeverity.HIGH

    lat_v = next(v for v in violations if v.metric_name == "latency_ms")
    assert lat_v.severity == IncidentSeverity.CRITICAL

def test_threshold_detector_service_down():
    snap = TelemetrySnapshot(
        service="order-service",
        pod_availability=0.0
    )
    violations = threshold_detector.evaluate(snap)
    assert any(v.metric_name == "pod_availability" and v.severity == IncidentSeverity.CRITICAL for v in violations)
