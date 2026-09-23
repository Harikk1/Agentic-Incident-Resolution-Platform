from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ServiceDependency(BaseModel):
    target_service: str
    dependency_type: str = "HTTP"  # HTTP | DATABASE | QUEUE
    healthy: bool = True
    latency_ms: float = 0.0
    failure_count: int = 0

class PodInfo(BaseModel):
    pod_id: str
    name: str
    namespace: str = "smartops"
    status: str = "Running"  # Running | Pending | CrashLoopBackOff | Terminating
    ready: bool = True
    restart_count: int = 0
    cpu_usage_cores: float = 0.05
    memory_usage_mb: float = 120.0
    node: str = "node-worker-1"

class ServiceInfo(BaseModel):
    service_id: str
    name: str
    namespace: str = "smartops"
    status: str = "HEALTHY"  # HEALTHY | DEGRADED | CRITICAL
    version: str = "v1.0.0"
    url: str
    desired_replicas: int = 2
    ready_replicas: int = 2
    available_replicas: int = 2
    pods: List[PodInfo] = Field(default_factory=list)
    dependencies: List[ServiceDependency] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
