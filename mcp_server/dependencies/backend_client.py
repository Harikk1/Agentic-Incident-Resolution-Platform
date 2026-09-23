"""
Shared SmartOps Domain Service client for MCP Tools.
Directly invokes SmartOps service layers (or API fallback) ensuring zero logic duplication.
"""
from typing import Dict, Any, List, Optional
from backend.app.database.repositories import services_repo, incidents_repo, kb_repo, audit_repo
from backend.app.monitoring.metric_buffer import metric_buffer
from backend.app.remediation.actions import remediation_actions
from backend.app.remediation.executor import remediation_executor
from backend.app.anomaly.detector import hybrid_detector
from backend.app.rca.engine import rca_engine
from backend.app.incidents.manager import incident_manager
from backend.app.models.remediation import RemediationPlan, RemediationActionType, RiskLevel
from backend.app.core.logging import logger

class SmartOpsDomainBridge:
    @staticmethod
    def get_service_metrics(service: str) -> Dict[str, Any]:
        snapshot = metric_buffer.get_latest(service)
        if not snapshot:
            return {"service": service, "status": "UNKNOWN", "metrics": {}}
        return snapshot.model_dump()

    @staticmethod
    def get_service_health(service: str) -> Dict[str, Any]:
        return remediation_actions.verify_service_health(service)

    @staticmethod
    def get_all_services() -> List[Dict[str, Any]]:
        return services_repo.list_all()

    @staticmethod
    def get_pod_status(service: str) -> List[Dict[str, Any]]:
        from backend.app.kubernetes.client import k8s_driver
        return k8s_driver.get_pods(service)

    @staticmethod
    def get_dependency_health(service: str) -> List[Dict[str, Any]]:
        svc = services_repo.get_by_id(service)
        if not svc:
            return []
        deps = svc.get("dependencies", [])
        results = []
        for d in deps:
            tgt = d.get("target_service")
            health = remediation_actions.verify_service_health(tgt) if tgt in {"user-service", "order-service", "payment-service"} else {"healthy": True}
            results.append({
                "target_service": tgt,
                "dependency_type": d.get("dependency_type", "HTTP"),
                "healthy": health.get("healthy", True),
                "latency_ms": d.get("latency_ms", 10.0)
            })
        return results

    @staticmethod
    def get_active_incidents() -> List[Dict[str, Any]]:
        return [i.model_dump() for i in incident_manager.get_active_incidents()]

    @staticmethod
    def get_incident(incident_id: str) -> Optional[Dict[str, Any]]:
        inc = incident_manager.get_incident(incident_id)
        return inc.model_dump() if inc else None

    @staticmethod
    def get_incident_history(service: str) -> List[Dict[str, Any]]:
        all_inc = incident_manager.list_all_incidents()
        return [i.model_dump() for i in all_inc if i.service == service]

    @staticmethod
    def search_logs(service: str, severity: Optional[str] = None, query: Optional[str] = None, limit: int = 30) -> List[Dict[str, Any]]:
        return logger.search_logs(service=service, severity=severity, query=query, limit=limit)

    @staticmethod
    def detect_anomaly(service: str) -> Dict[str, Any]:
        report = hybrid_detector.analyze_service(service)
        return report.to_dict()

    @staticmethod
    def predict_root_cause(service: str, incident_id: Optional[str] = None) -> Dict[str, Any]:
        snapshot = metric_buffer.get_latest(service)
        logs = logger.search_logs(service=service, limit=20)
        svc = services_repo.get_by_id(service)
        deps = svc.get("dependencies", []) if svc else []
        version = svc.get("version", "v1.0.0") if svc else "v1.0.0"

        rca_res = rca_engine.diagnose(snapshot, logs=logs, dependencies=deps, version=version)
        return rca_res.model_dump()

    @staticmethod
    def compare_with_baseline(service: str) -> Dict[str, Any]:
        snapshot = metric_buffer.get_latest(service)
        if not snapshot:
            return {"error": f"No telemetry available for {service}"}
        
        # Baselines
        baseline = {
            "latency_ms": 25.0,
            "request_rate": 50.0,
            "cpu_percent": 20.0,
            "memory_percent": 35.0,
            "error_rate": 0.005
        }
        deviations = {
            "latency_multiplier": round(snapshot.latency_ms / baseline["latency_ms"], 2),
            "request_rate_multiplier": round(snapshot.request_rate / baseline["request_rate"], 2),
            "cpu_diff": round(snapshot.cpu_percent - baseline["cpu_percent"], 1),
            "memory_diff": round(snapshot.memory_percent - baseline["memory_percent"], 1),
            "error_rate_diff": round(snapshot.error_rate - baseline["error_rate"], 4)
        }
        return {
            "service": service,
            "current": snapshot.model_dump(),
            "baseline": baseline,
            "deviations": deviations
        }

    @staticmethod
    def find_similar_incidents(service: str, query: str = "") -> List[Dict[str, Any]]:
        kb_docs = kb_repo.list_all()
        # Find matching documents
        matches = [d for d in kb_docs if d.get("service") == service or not service]
        return matches[:3]

    @staticmethod
    def execute_remediation(action: str, service: str, parameters: Dict[str, Any], actor: str = "AI_AGENT", approved: bool = True) -> Dict[str, Any]:
        risk_map = {
            "restart_service": RiskLevel.MEDIUM,
            "restart_pod": RiskLevel.LOW,
            "scale_service": RiskLevel.MEDIUM,
            "rollback_deployment": RiskLevel.HIGH,
            "increase_resources": RiskLevel.HIGH,
            "cleanup_disk": RiskLevel.LOW,
            "scale_consumers": RiskLevel.MEDIUM,
            "verify_service_health": RiskLevel.LOW
        }
        plan = RemediationPlan(
            action=RemediationActionType(action),
            service=service,
            parameters=parameters,
            risk_level=risk_map.get(action, RiskLevel.HIGH),
            reason=f"Executed via MCP tool by {actor}",
            expected_outcome="Remediates active anomaly"
        )
        res = remediation_executor.execute_plan(plan, actor=actor, approved=approved, approved_by=actor)
        return res.model_dump()

bridge = SmartOpsDomainBridge()
