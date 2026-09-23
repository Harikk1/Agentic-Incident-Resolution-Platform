import pytest
from backend.app.models.metric import TelemetrySnapshot
from backend.app.anomaly.statistical import statistical_detector
from backend.app.anomaly.isolation_forest import ml_anomaly_detector
from backend.app.anomaly.detector import hybrid_detector

def test_statistical_zscore_detection():
    history = [20.0, 21.0, 19.5, 20.5, 20.0, 21.5, 20.2, 19.8, 20.1, 20.3]
    # Current value spikes to 85.0
    res = statistical_detector.detect_zscore(85.0, history, "cpu_percent")
    assert res.is_anomaly is True
    assert res.z_score > 3.0

def test_ml_isolation_forest_detection():
    snap_normal = TelemetrySnapshot(
        service="payment-service",
        cpu_percent=22.0,
        memory_percent=36.0,
        disk_percent=40.0,
        request_rate=52.0,
        latency_ms=24.0,
        error_rate=0.002
    )
    res_normal = ml_anomaly_detector.detect(snap_normal)
    assert res_normal.is_anomaly is False

    # Highly anomalous multivariate vector
    snap_abnormal = TelemetrySnapshot(
        service="payment-service",
        cpu_percent=95.0,
        memory_percent=96.0,
        disk_percent=92.0,
        request_rate=850.0,
        latency_ms=380.0,
        error_rate=0.15
    )
    res_abnormal = ml_anomaly_detector.detect(snap_abnormal)
    assert res_abnormal.is_anomaly is True
    assert len(res_abnormal.affected_features) > 0

def test_hybrid_detector_orchestration():
    snap = TelemetrySnapshot(
        service="payment-service",
        cpu_percent=92.0,
        latency_ms=180.0
    )
    report = hybrid_detector.analyze_service("payment-service", snap)
    assert report.is_anomalous is True
    assert report.severity.value in ["HIGH", "CRITICAL"]
    assert len(report.threshold_violations) > 0
