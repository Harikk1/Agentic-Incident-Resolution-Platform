import time
import asyncio
from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.monitoring.metric_buffer import metric_buffer
from backend.app.monitoring.prometheus_client import prom_client
from backend.app.database.repositories import services_repo
from backend.app.models.metric import TelemetrySnapshot

from backend.app.anomaly.detector import hybrid_detector
from backend.app.incidents.manager import incident_manager
from backend.app.models.incident import IncidentState, IncidentSeverity
from backend.app.models.remediation import RiskLevel
from backend.app.rca.engine import rca_engine
from backend.app.remediation.policy import policy_engine

class MetricCollector:
    def __init__(self):
        self.is_running = False
        self._task = None

    async def collect_snapshot(self, service_name: str, service_url: str) -> TelemetrySnapshot:
        snapshot = await prom_client.fetch_service_telemetry(service_name, service_url)
        # Store in buffer
        metric_buffer.add_snapshot(service_name, snapshot)
        return snapshot

    async def evaluate_mode_a(self, service_name: str, snapshot: TelemetrySnapshot, service_info: Dict[str, Any]):
        """Mode A: Automated Anomaly Detection, Incident Creation, RCA, and Remediation Routing."""
        try:
            # 1. Evaluate Anomaly using 3-tier Hybrid Anomaly Detector
            report = hybrid_detector.analyze_service(service_name, snapshot)
            if not report.is_anomalous:
                return

            # 2. Check if an active unresolved incident already exists for this service
            existing = incident_manager.get_active_incident_for_service(service_name)
            if existing:
                return

            # 3. Create Incident (DETECTED)
            symptoms = [v.get("message", str(v)) for v in report.threshold_violations] or [report.summary]
            inc = incident_manager.create_incident(
                service=service_name,
                title=f"Anomaly on {service_name}: {report.summary}",
                severity=report.severity,
                symptoms=symptoms,
                metrics=snapshot.model_dump()
            )
            logger.info(f"[Mode A] Anomaly detected: created incident {inc.incident_id} for {service_name}")

            # 4. Autonomous Investigation (INVESTIGATING)
            logs = logger.search_logs(service=service_name, limit=30)
            inc = incident_manager.transition_state(
                inc.incident_id,
                IncidentState.INVESTIGATING,
                actor="AUTO_AIOPS",
                message=f"Autonomous investigation started: {report.summary}",
                details={"logs_count": len(logs)}
            )
            inc.logs = logs

            # 5. Autonomous RCA Diagnosis (DIAGNOSED)
            version = service_info.get("version", "v1.0.0")
            rca_res = rca_engine.diagnose(snapshot, logs=logs, version=version)
            inc.rca = rca_res

            if rca_res.confidence >= 0.50:
                inc = incident_manager.transition_state(
                    inc.incident_id,
                    IncidentState.DIAGNOSED,
                    actor="AUTO_AIOPS",
                    message=f"Root cause diagnosed as {rca_res.root_cause.value} ({int(rca_res.confidence * 100)}% confidence)."
                )
                inc.rca = rca_res
                inc.logs = logs

                # 6. Select Remediation via Deterministic Policy Engine
                plan = policy_engine.select_remediation(inc)
                if plan:
                    approval_required = (plan.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH])

                    if approval_required:
                        # 7. Gate by Human Approval -> WAITING_APPROVAL (Approval Queue)
                        inc = incident_manager.transition_state(
                            inc.incident_id,
                            IncidentState.WAITING_APPROVAL,
                            actor="POLICY_ENGINE",
                            message=f"Proposed action '{plan.action.value}' carries {plan.risk_level.value} risk. Sent to Remediation Approval Queue."
                        )
                        logger.info(f"[Mode A] Incident {inc.incident_id} placed in Approval Queue (action: {plan.action.value}, risk: {plan.risk_level.value})")
                    else:
                        inc = incident_manager.transition_state(
                            inc.incident_id,
                            IncidentState.REMEDIATION_PROPOSED,
                            actor="POLICY_ENGINE",
                            message=f"Safe policy proposed: '{plan.action.value}'. Executing automated remediation."
                        )
                        remediation_executor.execute_plan(
                            plan=plan,
                            actor="AUTO_POLICY",
                            incident_id=inc.incident_id,
                            approved=True
                        )
                    inc.recommended_action = plan.action.value
                    inc.action_parameters = plan.parameters
                    inc.risk_level = plan.risk_level.value
                    inc.approval_required = approval_required
            else:
                inc = incident_manager.transition_state(
                    inc.incident_id,
                    IncidentState.NEEDS_HUMAN_REVIEW,
                    actor="AUTO_AIOPS",
                    message=f"Root cause confidence ({rca_res.confidence:.2f}) below threshold. Escalated to on-call engineer."
                )

            # Preserve RCA, logs, and remediation fields on the persisted incident
            latest_inc = incident_manager.get_incident(inc.incident_id)
            if latest_inc:
                latest_inc.rca = rca_res
                latest_inc.logs = logs
                latest_inc.recommended_action = inc.recommended_action
                latest_inc.action_parameters = inc.action_parameters
                latest_inc.risk_level = inc.risk_level
                latest_inc.approval_required = inc.approval_required
                incident_manager.save_incident(latest_inc)

        except Exception as e:
            logger.error(f"[Mode A] Error in automated incident evaluation for {service_name}: {e}")

    async def collect_all(self):
        services = services_repo.list_all()
        for svc in services:
            svc_name = svc["name"]
            svc_url = svc["url"]
            snapshot = await self.collect_snapshot(svc_name, svc_url)
            await self.evaluate_mode_a(svc_name, snapshot, svc)

    async def _loop(self, interval_seconds: int = 5):
        self.is_running = True
        logger.info("SmartOps Telemetry Collector background task started")
        while self.is_running:
            try:
                await self.collect_all()
            except Exception as e:
                logger.error(f"Collector iteration error: {e}")
            await asyncio.sleep(interval_seconds)

    def start(self):
        if not self.is_running:
            self._task = asyncio.create_task(self._loop())

    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()

collector = MetricCollector()
