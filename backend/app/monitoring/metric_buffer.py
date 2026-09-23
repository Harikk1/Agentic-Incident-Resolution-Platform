import time
import threading
from typing import Dict, List, Optional
from backend.app.models.metric import TelemetrySnapshot

class ServiceMetricBuffer:
    def __init__(self, max_points: int = 120):
        self.max_points = max_points
        self._buffers: Dict[str, List[TelemetrySnapshot]] = {}
        self._lock = threading.Lock()

    def add_snapshot(self, service: str, snapshot: TelemetrySnapshot):
        with self._lock:
            if service not in self._buffers:
                self._buffers[service] = []
            self._buffers[service].append(snapshot)
            if len(self._buffers[service]) > self.max_points:
                self._buffers[service].pop(0)

    def get_latest(self, service: str) -> Optional[TelemetrySnapshot]:
        with self._lock:
            buf = self._buffers.get(service)
            if buf:
                return buf[-1]
            return None

    def get_history(self, service: str, count: Optional[int] = None) -> List[TelemetrySnapshot]:
        with self._lock:
            buf = self._buffers.get(service, [])
            if count and count < len(buf):
                return list(buf[-count:])
            return list(buf)

    def get_all_services(self) -> List[str]:
        with self._lock:
            return list(self._buffers.keys())

    def clear(self, service: Optional[str] = None):
        with self._lock:
            if service:
                self._buffers.pop(service, None)
            else:
                self._buffers.clear()

metric_buffer = ServiceMetricBuffer()
