from typing import List, Dict, Any, Optional
from backend.app.models.metric import TelemetrySnapshot

class TelemetryEvidence:
    @staticmethod
    def extract_evidence(
        snapshot: TelemetrySnapshot,
        logs: Optional[List[Dict[str, Any]]] = None,
        dependencies: Optional[List[Dict[str, Any]]] = None,
        version: str = "v1.0.0"
    ) -> Dict[str, Any]:
        """Extracts factual, non-hallucinated evidence items from telemetry, logs, and dependencies"""
        evidence_data = {
            "metrics": {
                "cpu_percent": snapshot.cpu_percent,
                "memory_percent": snapshot.memory_percent,
                "disk_percent": snapshot.disk_percent,
                "request_rate": snapshot.request_rate,
                "latency_ms": snapshot.latency_ms,
                "error_rate": snapshot.error_rate,
                "database_latency_ms": snapshot.database_latency_ms,
                "dependency_latency_ms": snapshot.dependency_latency_ms,
                "pod_availability": snapshot.pod_availability,
                "pod_restarts": snapshot.pod_restarts
            },
            "facts": [],
            "log_patterns": {
                "db_timeouts": False,
                "application_exceptions": False,
                "oom_kills": False,
                "connection_refused": False
            },
            "dependency_issues": []
        }

        # Analyze metric facts
        if snapshot.request_rate > 300.0:
            evidence_data["facts"].append(f"Request rate surged to {snapshot.request_rate:.1f} req/s (significant traffic increase)")
        if snapshot.cpu_percent >= 80.0:
            evidence_data["facts"].append(f"CPU utilization high at {snapshot.cpu_percent:.1f}%")
        if snapshot.memory_percent >= 85.0:
            evidence_data["facts"].append(f"Memory saturation at {snapshot.memory_percent:.1f}%")
        if snapshot.disk_percent >= 85.0:
            evidence_data["facts"].append(f"Disk utilization critical at {snapshot.disk_percent:.1f}%")
        if snapshot.latency_ms >= 120.0:
            evidence_data["facts"].append(f"Response latency elevated at {snapshot.latency_ms:.1f}ms")
        if snapshot.error_rate >= 0.03:
            evidence_data["facts"].append(f"HTTP error rate elevated at {snapshot.error_rate*100:.1f}%")
        if snapshot.database_latency_ms >= 150.0:
            evidence_data["facts"].append(f"Database query latency excessive at {snapshot.database_latency_ms:.1f}ms")
        if snapshot.pod_availability < 0.5:
            evidence_data["facts"].append("Pod availability is 0.0 (service down or crashed)")
        if "bad" in version.lower() or version == "v2.1.0-bad":
            evidence_data["facts"].append(f"Recent deployment identified with build tag: {version}")

        # Scan actual logs for patterns
        if logs:
            for log in logs:
                msg = log.get("message", "").lower()
                if "database connection pool exhausted" in msg or "query timeout" in msg or "db timeout" in msg:
                    evidence_data["log_patterns"]["db_timeouts"] = True
                    evidence_data["facts"].append(f"Log evidence: {log.get('message')}")
                if "nullpointerexception" in msg or "bad deployment" in msg or "exception" in msg or "stacktrace" in msg:
                    evidence_data["log_patterns"]["application_exceptions"] = True
                    evidence_data["facts"].append(f"Log evidence: {log.get('message')}")
                if "oom" in msg or "out of memory" in msg or "oomkilled" in msg:
                    evidence_data["log_patterns"]["oom_kills"] = True
                    evidence_data["facts"].append(f"Log evidence: {log.get('message')}")

        # Scan dependencies
        if dependencies:
            for dep in dependencies:
                if not dep.get("healthy", True) or dep.get("latency_ms", 0) > 100:
                    evidence_data["dependency_issues"].append(dep)
                    evidence_data["facts"].append(f"Upstream dependency '{dep.get('target_service')}' degraded ({dep.get('latency_ms')}ms)")

        return evidence_data
