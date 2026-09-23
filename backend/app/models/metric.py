import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class TelemetrySnapshot(BaseModel):
    service: str
    timestamp: float = Field(default_factory=time.time)
    cpu_percent: float = 15.0
    memory_percent: float = 35.0
    disk_percent: float = 40.0
    request_rate: float = 50.0  # requests per second
    latency_ms: float = 25.0    # average response latency
    error_rate: float = 0.0     # 0.0 to 1.0 (e.g. 0.02 = 2%)
    http_4xx_count: int = 0
    http_5xx_count: int = 0
    active_requests: int = 5
    pod_restarts: int = 0
    pod_availability: float = 1.0  # 1.0 = 100% available
    desired_replicas: int = 2
    ready_replicas: int = 2
    database_latency_ms: float = 10.0
    dependency_latency_ms: float = 15.0

class MetricTimeSeriesPoint(BaseModel):
    timestamp: float
    value: float

class ServiceMetricsSummary(BaseModel):
    service: str
    current: TelemetrySnapshot
    baseline_latency_ms: float = 25.0
    baseline_request_rate: float = 50.0
    baseline_cpu_percent: float = 20.0
    baseline_memory_percent: float = 35.0
    baseline_error_rate: float = 0.005
    is_anomalous: bool = False
