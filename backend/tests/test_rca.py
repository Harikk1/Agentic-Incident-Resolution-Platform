import pytest
from backend.app.models.metric import TelemetrySnapshot
from backend.app.models.incident import RootCause
from backend.app.rca.engine import rca_engine

def test_rca_traffic_spike():
    snap = TelemetrySnapshot(
        service="payment-service",
        request_rate=650.0,
        cpu_percent=88.0,
        latency_ms=175.0,
        database_latency_ms=25.0
    )
    res = rca_engine.diagnose(snap)
    assert res.root_cause == RootCause.TRAFFIC_SPIKE
    assert res.confidence >= 0.80
    assert any("Request rate" in e for e in res.evidence)

def test_rca_database_bottleneck():
    snap = TelemetrySnapshot(
        service="payment-service",
        request_rate=60.0,
        cpu_percent=32.0,      # CPU is normal!
        latency_ms=280.0,      # API latency is high
        database_latency_ms=360.0 # DB latency is excessive
    )
    logs = [{"message": "Database connection pool exhausted: query timeout", "level": "WARN"}]
    res = rca_engine.diagnose(snap, logs=logs)
    assert res.root_cause == RootCause.DATABASE_BOTTLENECK
    assert res.confidence >= 0.85

def test_rca_memory_leak():
    snap = TelemetrySnapshot(
        service="payment-service",
        memory_percent=94.0,
        pod_restarts=3
    )
    logs = [{"message": "Container OOMKilled by cgroup", "level": "CRITICAL"}]
    res = rca_engine.diagnose(snap, logs=logs)
    assert res.root_cause == RootCause.MEMORY_LEAK
    assert res.confidence >= 0.85

def test_rca_bad_deployment():
    snap = TelemetrySnapshot(
        service="payment-service",
        error_rate=0.09,
        latency_ms=80.0
    )
    logs = [{"message": "NullPointerException in payment.execute: regression", "level": "ERROR"}]
    res = rca_engine.diagnose(snap, logs=logs, version="v2.1.0-bad")
    assert res.root_cause == RootCause.BAD_DEPLOYMENT
    assert res.confidence >= 0.80

def test_rca_insufficient_evidence_returns_unknown():
    snap = TelemetrySnapshot(
        service="user-service",
        cpu_percent=25.0,
        memory_percent=38.0,
        latency_ms=28.0,
        error_rate=0.001
    )
    res = rca_engine.diagnose(snap)
    assert res.root_cause == RootCause.UNKNOWN
