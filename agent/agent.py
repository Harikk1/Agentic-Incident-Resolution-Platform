from typing import Dict, Any, Optional
from agent.state import AgentState
from agent.graph import AgentWorkflowEngine
from backend.app.database.repositories import session_repo

class SmartOpsAgent:
    """High-level SmartOps AI Agent Interface"""

    def process_message(
        self,
        user_message: str,
        session_id: str,
        approved: bool = False,
        action_override: Optional[str] = None
    ) -> AgentState:
        # Initialize state
        state = AgentState(user_request=user_message)
        
        # Step 1: Understand
        state = AgentWorkflowEngine.step_understand_request(state)

        # Step 2 & 3: Context Collection via MCP Tools
        state = AgentWorkflowEngine.step_collect_context(state)

        # Step 4: Analyze
        state = AgentWorkflowEngine.step_analyze(state)

        # Step 5: Diagnose (RCA & RAG)
        state = AgentWorkflowEngine.step_diagnose(state)

        # Step 6: Plan Remediation
        state = AgentWorkflowEngine.step_plan_remediation(state)

        # Handle user approval if granted
        if approved:
            state.approval_status = "APPROVED"
            if action_override:
                state.recommended_action = action_override

        # Step 7 & 8: Execute and Verify
        state = AgentWorkflowEngine.step_execute_and_verify(state)

        # Step 9: Final Response Generation
        state = AgentWorkflowEngine.step_final_response(state)

        # Sync with Incident Management & Approval Queue
        from backend.app.incidents.manager import incident_manager
        from backend.app.models.incident import IncidentState, IncidentSeverity
        svc = state.service
        if svc:
            if state.approval_status == "PENDING" and state.recommended_action:
                inc = incident_manager.get_active_incident_for_service(svc)
                if not inc:
                    inc = incident_manager.create_incident(
                        service=svc,
                        title=f"AI Agent Investigation on {svc}: {user_message[:60]}",
                        severity=IncidentSeverity.CRITICAL if state.risk_level == "HIGH" else IncidentSeverity.HIGH,
                        symptoms=state.evidence or ["Investigated by SmartOps AI Agent"],
                        metrics=state.metrics or {}
                    )
                inc.recommended_action = state.recommended_action
                inc.action_parameters = state.action_parameters
                inc.risk_level = state.risk_level
                inc.approval_required = True
                if inc.status == IncidentState.DETECTED:
                    incident_manager.transition_state(
                        inc.incident_id,
                        IncidentState.INVESTIGATING,
                        actor="SMARTOPS_AGENT",
                        message=f"Agent investigation initiated for {svc}."
                    )
                if inc.status == IncidentState.INVESTIGATING:
                    incident_manager.transition_state(
                        inc.incident_id,
                        IncidentState.DIAGNOSED,
                        actor="SMARTOPS_AGENT",
                        message=f"Agent diagnosed root cause for {svc}."
                    )
                if inc.status == IncidentState.DIAGNOSED:
                    incident_manager.transition_state(
                        inc.incident_id,
                        IncidentState.WAITING_APPROVAL,
                        actor="SMARTOPS_AGENT",
                        message=f"Agent proposed '{state.recommended_action}' ({state.risk_level} risk). Sent to Remediation Approval Queue."
                    )
                incident_manager.save_incident(inc)
                if state.approval_card:
                    state.approval_card["incident_id"] = inc.incident_id
            elif approved:
                inc = incident_manager.get_active_incident_for_service(svc)
                if inc and inc.status != IncidentState.RESOLVED:
                    if inc.status == IncidentState.WAITING_APPROVAL:
                        incident_manager.transition_state(
                            inc.incident_id,
                            IncidentState.REMEDIATION_EXECUTING,
                            actor="SMARTOPS_AGENT",
                            message=f"Executing '{state.recommended_action}'."
                        )
                    if inc.status == IncidentState.REMEDIATION_EXECUTING:
                        incident_manager.transition_state(
                            inc.incident_id,
                            IncidentState.VERIFYING,
                            actor="SMARTOPS_AGENT",
                            message="Verifying post-remediation telemetry."
                        )
                    if inc.status == IncidentState.VERIFYING:
                        incident_manager.transition_state(
                            inc.incident_id,
                            IncidentState.RESOLVED,
                            actor="SMARTOPS_AGENT",
                            message=f"Action '{state.recommended_action}' approved & executed in chat session. Verified healthy.",
                            details=state.verification_result or {}
                        )

        # Save session history
        session = session_repo.get_by_id(session_id) or {"session_id": session_id, "messages": [], "actions": []}
        session["messages"].append({"role": "user", "content": user_message})
        session["messages"].append({
            "role": "assistant",
            "content": state.final_response,
            "tool_traces": [t.model_dump() for t in state.tool_traces],
            "approval_card": state.approval_card,
            "verification": state.verification_result
        })
        session_repo.save(session)

        return state

smartops_agent = SmartOpsAgent()
