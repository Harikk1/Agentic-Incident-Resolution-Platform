import time
import uuid
from typing import Dict, Any, Optional
from backend.app.models.remediation import (
    RemediationActionType, RemediationPlan, RemediationExecutionResult, RiskLevel
)
from backend.app.models.incident import IncidentState
from backend.app.remediation.actions import remediation_actions
from backend.app.database.repositories import audit_repo, remediation_repo
from backend.app.incidents.manager import incident_manager
from backend.app.core.logging import logger

class RemediationExecutor:
    def execute_plan(
        self,
        plan: RemediationPlan,
        actor: str = "SYSTEM",
        incident_id: Optional[str] = None,
        approved: bool = False,
        approved_by: Optional[str] = None
    ) -> RemediationExecutionResult:
        start_time = time.time()
        action_id = f"ACT-{uuid.uuid4().hex[:6].upper()}"

        # Risk & Approval Guardrails
        if plan.risk_level == RiskLevel.HIGH and not approved:
            raise PermissionError(f"Action '{plan.action.value}' carries HIGH risk and requires explicit human approval.")
        
        if plan.risk_level == RiskLevel.MEDIUM and not approved and actor != "AUTO_POLICY":
            raise PermissionError(f"Action '{plan.action.value}' carries MEDIUM risk and requires human approval.")

        # Update Incident to REMEDIATION_EXECUTING
        if incident_id:
            incident_manager.transition_state(
                incident_id,
                IncidentState.REMEDIATION_EXECUTING,
                actor=actor,
                message=f"Executing remediation action '{plan.action.value}' on {plan.service}",
                details={"action": plan.action.value, "parameters": plan.parameters}
            )

        status = "SUCCESS"
        message = ""
        verification = {}
        health_verified = False

        try:
            # Dispatch to safe actions
            if plan.action == RemediationActionType.SCALE_SERVICE:
                replicas = plan.parameters.get("replicas", 3)
                remediation_actions.scale_service(plan.service, replicas)
                message = f"Scaled {plan.service} to {replicas} replicas"

            elif plan.action == RemediationActionType.RESTART_SERVICE:
                remediation_actions.restart_service(plan.service)
                message = f"Restarted service deployment {plan.service}"

            elif plan.action == RemediationActionType.RESTART_POD:
                remediation_actions.restart_pod(plan.service, plan.parameters.get("pod_name"))
                message = f"Restarted unhealthy pod for {plan.service}"

            elif plan.action == RemediationActionType.ROLLBACK_DEPLOYMENT:
                remediation_actions.rollback_deployment(plan.service)
                message = f"Rolled back {plan.service} to previous stable revision"

            elif plan.action == RemediationActionType.INCREASE_RESOURCES:
                cpu = plan.parameters.get("cpu_request", "1000m")
                mem = plan.parameters.get("memory_request", "1Gi")
                remediation_actions.increase_resources(plan.service, cpu, mem)
                message = f"Increased resources for {plan.service} to cpu={cpu}, mem={mem}"

            elif plan.action == RemediationActionType.CLEANUP_DISK:
                remediation_actions.cleanup_disk(plan.service)
                message = f"Cleaned up disk cache on {plan.service}"

            elif plan.action == RemediationActionType.VERIFY_SERVICE_HEALTH:
                pass  # Verification executed below

            # Transition to VERIFYING
            if incident_id:
                incident_manager.transition_state(
                    incident_id,
                    IncidentState.VERIFYING,
                    actor=actor,
                    message="Verifying health and telemetry stabilization post-remediation"
                )

            # Health Verification
            verification = remediation_actions.verify_service_health(plan.service)
            health_verified = verification.get("healthy", False)

            if health_verified:
                if incident_id:
                    incident_manager.transition_state(
                        incident_id,
                        IncidentState.RESOLVED,
                        actor=actor,
                        message=f"Incident resolved. Verification confirmed service healthy.",
                        details=verification
                    )
            else:
                status = "FAILED"
                message += " - Verification failed: Service health check did not pass"
                if incident_id:
                    incident_manager.transition_state(
                        incident_id,
                        IncidentState.REMEDIATION_FAILED,
                        actor=actor,
                        message="Remediation executed but post-verification failed"
                    )

        except Exception as e:
            status = "FAILED"
            message = f"Execution failed: {str(e)}"
            if incident_id:
                incident_manager.transition_state(
                    incident_id,
                    IncidentState.REMEDIATION_FAILED,
                    actor=actor,
                    message=f"Remediation error: {str(e)}"
                )

        exec_duration = time.time() - start_time

        result = RemediationExecutionResult(
            action_id=action_id,
            incident_id=incident_id,
            action=plan.action,
            service=plan.service,
            parameters=plan.parameters,
            status=status,
            message=message,
            health_verified=health_verified,
            verification_details=verification,
            execution_time_seconds=round(exec_duration, 2)
        )

        # Store action record
        remediation_repo.save(result.model_dump())

        # Write immutable Audit Log (Section 23 & 38)
        audit_repo.save({
            "action_id": action_id,
            "incident_id": incident_id,
            "actor": actor,
            "tool": plan.action.value,
            "parameters": plan.parameters,
            "risk": plan.risk_level.value,
            "approved": approved,
            "approved_by": approved_by,
            "result": status,
            "details": message,
            "timestamp": time.time(),
            "iso_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

        return result

remediation_executor = RemediationExecutor()
