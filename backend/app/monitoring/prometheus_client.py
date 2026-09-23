import time
import httpx
from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models.metric import TelemetrySnapshot

class PrometheusClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.PROMETHEUS_URL

    async def query(self, expr: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/api/v1/query"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(url, params={"query": expr})
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass
        return None

    async def fetch_service_telemetry(self, service_name: str, service_url: str) -> TelemetrySnapshot:
        """Pulls telemetry directly from microservice endpoints or queries Prometheus"""
        snapshot = TelemetrySnapshot(service=service_name)
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                # 1. Health endpoint
                health_resp = await client.get(f"{service_url}/health")
                if health_resp.status_code == 200:
                    data = health_resp.json()
                    snapshot.pod_availability = 1.0 if data.get("status") == "UP" else 0.0
                else:
                    snapshot.pod_availability = 0.0

                # 2. Check if faults active on service
                fault_resp = await client.get(f"{service_url}/api/faults")
                if fault_resp.status_code == 200:
                    faults = fault_resp.json()
                    if faults.get("latency_ms", 0) > 0:
                        snapshot.latency_ms = 25.0 + float(faults["latency_ms"])
                    if faults.get("error_rate", 0) > 0:
                        snapshot.error_rate = float(faults["error_rate"])
                    if faults.get("cpu_burn"):
                        snapshot.cpu_percent = 92.0
                    if faults.get("memory_leak"):
                        snapshot.memory_percent = 94.0
                    if faults.get("db_bottleneck"):
                        snapshot.database_latency_ms = 380.0
                        snapshot.latency_ms = max(snapshot.latency_ms, 260.0)
                    if faults.get("bad_deployment"):
                        snapshot.error_rate = max(snapshot.error_rate, 0.08)

        except Exception as e:
            logger.debug(f"Direct scrape of {service_name} at {service_url} encountered error: {e}")
            snapshot.pod_availability = 0.0

        return snapshot

prom_client = PrometheusClient()
