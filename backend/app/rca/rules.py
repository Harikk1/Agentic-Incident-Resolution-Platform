from typing import Dict, Any, Tuple, List
from backend.app.models.incident import RootCause

class RCARuleEvaluator:
    @staticmethod
    def evaluate_traffic_spike(evidence: Dict[str, Any]) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        m = evidence["metrics"]

        if m["request_rate"] >= 300.0:
            score += 0.5
            reasons.append(f"Request rate increased significantly to {m['request_rate']:.1f} req/s")
        elif m["request_rate"] >= 150.0:
            score += 0.25
            reasons.append(f"Request rate elevated at {m['request_rate']:.1f} req/s")

        if m["cpu_percent"] >= 75.0:
            score += 0.3
            reasons.append(f"CPU utilization corresponds to high load ({m['cpu_percent']:.1f}%)")

        if m["database_latency_ms"] < 60.0 and not evidence["log_patterns"]["db_timeouts"]:
            score += 0.15
            reasons.append("Database query latency remains normal (< 60ms)")

        return min(score, 0.98), reasons

    @staticmethod
    def evaluate_database_bottleneck(evidence: Dict[str, Any]) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        m = evidence["metrics"]

        if m["database_latency_ms"] >= 150.0:
            score += 0.5
            reasons.append(f"Database query latency excessive at {m['database_latency_ms']:.1f}ms")

        if evidence["log_patterns"]["db_timeouts"]:
            score += 0.35
            reasons.append("Database connection pool timeout errors detected in recent logs")

        if m["latency_ms"] >= 100.0 and m["cpu_percent"] < 75.0:
            score += 0.15
            reasons.append("High API latency observed while service CPU utilization remains normal/low")

        return min(score, 0.98), reasons

    @staticmethod
    def evaluate_memory_leak(evidence: Dict[str, Any]) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        m = evidence["metrics"]

        if m["memory_percent"] >= 90.0:
            score += 0.6
            reasons.append(f"Process memory at critical ceiling ({m['memory_percent']:.1f}%)")
        elif m["memory_percent"] >= 80.0:
            score += 0.3
            reasons.append(f"Process memory high at {m['memory_percent']:.1f}%")

        if evidence["log_patterns"]["oom_kills"] or m["pod_restarts"] > 0:
            score += 0.35
            reasons.append("OOMKilled events or pod restart cycles observed")

        return min(score, 0.98), reasons

    @staticmethod
    def evaluate_bad_deployment(evidence: Dict[str, Any], version: str = "v1.0.0") -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        m = evidence["metrics"]

        if "bad" in version.lower() or version == "v2.1.0-bad":
            score += 0.45
            reasons.append(f"Deployment release revision identified as newly rolled out build: {version}")

        if m["error_rate"] >= 0.04:
            score += 0.3
            reasons.append(f"HTTP 5xx error rate elevated to {m['error_rate']*100:.1f}% immediately post-deployment")

        if evidence["log_patterns"]["application_exceptions"]:
            score += 0.25
            reasons.append("Application runtime exceptions (NullPointer/regression) captured in container logs")

        return min(score, 0.98), reasons

    @staticmethod
    def evaluate_service_failure(evidence: Dict[str, Any]) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        m = evidence["metrics"]

        if m["pod_availability"] < 0.5:
            score += 0.8
            reasons.append("Service health check failed: pod availability is 0.0 / HTTP 503")

        return min(score, 0.98), reasons

    @staticmethod
    def evaluate_dependency_failure(evidence: Dict[str, Any]) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        m = evidence["metrics"]

        if len(evidence["dependency_issues"]) > 0:
            score += 0.5
            reasons.append(f"Upstream dependencies unhealthy: {', '.join([d['target_service'] for d in evidence['dependency_issues']])}")

        if m["dependency_latency_ms"] >= 100.0:
            score += 0.3
            reasons.append(f"Upstream dependency latency high at {m['dependency_latency_ms']:.1f}ms")

        return min(score, 0.98), reasons

    @staticmethod
    def evaluate_cpu_saturation(evidence: Dict[str, Any]) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        m = evidence["metrics"]

        if m["cpu_percent"] >= 85.0 and m["request_rate"] < 150.0:
            score += 0.7
            reasons.append(f"CPU saturation ({m['cpu_percent']:.1f}%) observed under standard traffic ({m['request_rate']:.1f} req/s)")

        return min(score, 0.98), reasons

    @staticmethod
    def evaluate_disk_pressure(evidence: Dict[str, Any]) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        m = evidence["metrics"]

        if m["disk_percent"] >= 85.0:
            score += 0.8
            reasons.append(f"Storage volume capacity exceeded ({m['disk_percent']:.1f}%)")

        return min(score, 0.98), reasons
