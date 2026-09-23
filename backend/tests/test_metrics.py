import pytest
from backend.app.models.metric import TelemetrySnapshot
from backend.app.monitoring.metric_buffer import ServiceMetricBuffer

def test_metric_buffer_add_and_retrieve():
    buf = ServiceMetricBuffer(max_points=5)
    s1 = TelemetrySnapshot(service="test-svc", cpu_percent=25.0)
    s2 = TelemetrySnapshot(service="test-svc", cpu_percent=30.0)

    buf.add_snapshot("test-svc", s1)
    buf.add_snapshot("test-svc", s2)

    latest = buf.get_latest("test-svc")
    assert latest is not None
    assert latest.cpu_percent == 30.0

    history = buf.get_history("test-svc")
    assert len(history) == 2

def test_metric_buffer_capacity_eviction():
    buf = ServiceMetricBuffer(max_points=3)
    for i in range(5):
        buf.add_snapshot("test-svc", TelemetrySnapshot(service="test-svc", cpu_percent=float(i)))

    history = buf.get_history("test-svc")
    assert len(history) == 3
    # Oldest 0 and 1 should have been popped
    assert history[0].cpu_percent == 2.0
    assert history[-1].cpu_percent == 4.0
