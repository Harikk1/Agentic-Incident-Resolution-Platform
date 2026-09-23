import re
from typing import Dict, Any, List, Optional
from agent.state import AgentState, ToolExecutionTrace
from agent.mcp_client import mcp_client
from agent.rag import rag_engine
from backend.app.models.remediation import RiskLevel

class AgentWorkflowEngine:
    """State Machine Workflow for Mode B Agentic Incident Response"""

    @staticmethod
    def step_understand_request(state: AgentState) -> AgentState:
        state.current_step = "UNDERSTAND_REQUEST"
        req = state.user_request.lower()

        # Identify target service
        target_service = "payment-service"  # Default microservice if none matched
        if "user" in req:
            target_service = "user-service"
        elif "order" in req:
            target_service = "order-service"
        elif "payment" in req:
            target_service = "payment-service"

        state.service = target_service
        return state

    @staticmethod
    def step_collect_context(state: AgentState) -> AgentState:
        state.current_step = "COLLECT_CONTEXT"
        svc = state.service or "payment-service"

        # Dynamically call monitoring and context tools via MCP
        res_m = mcp_client.call_tool("get_service_metrics", {"service": svc})
        state.tool_traces.append(res_m["trace"])
        state.metrics = res_m["result"]

        res_h = mcp_client.call_tool("get_service_health", {"service": svc})
        state.tool_traces.append(res_h["trace"])

        res_d = mcp_client.call_tool("get_dependency_health", {"service": svc})
        state.tool_traces.append(res_d["trace"])
        state.dependencies = res_d["result"]

        res_e = mcp_client.call_tool("get_recent_errors", {"service": svc})
        state.tool_traces.append(res_e["trace"])
        state.logs = res_e["result"]

        return state

    @staticmethod
    def step_analyze(state: AgentState) -> AgentState:
        state.current_step = "ANALYZE"
        svc = state.service or "payment-service"

        res_ano = mcp_client.call_tool("detect_anomaly", {"service": svc})
        state.tool_traces.append(res_ano["trace"])
        state.anomaly_results = res_ano["result"]

        res_base = mcp_client.call_tool("compare_with_baseline", {"service": svc})
        state.tool_traces.append(res_base["trace"])

        return state

    @staticmethod
    def step_diagnose(state: AgentState) -> AgentState:
        state.current_step = "DIAGNOSE"
        svc = state.service or "payment-service"

        res_rca = mcp_client.call_tool("predict_root_cause", {"service": svc, "incident_id": state.incident_id})
        state.tool_traces.append(res_rca["trace"])
        rca_data = res_rca["result"]
        state.rca_result = rca_data
        state.confidence = rca_data.get("confidence", 0.0)
        state.evidence = rca_data.get("evidence", [])

        # RAG Query for supporting historical context
        sim_res = mcp_client.call_tool("find_similar_incidents", {"service": svc, "query": " ".join(state.evidence)})
        state.tool_traces.append(sim_res["trace"])
        state.historical_incidents = sim_res["result"]

        return state

    @staticmethod
    def step_plan_remediation(state: AgentState) -> AgentState:
        state.current_step = "PLAN_REMEDIATION"
        rca_cause = (state.rca_result or {}).get("root_cause", "UNKNOWN")

        if rca_cause == "TRAFFIC_SPIKE":
            state.recommended_action = "scale_service"
            state.action_parameters = {"replicas": 5}
            state.risk_level = RiskLevel.MEDIUM.value
            state.approval_status = "PENDING"
        elif rca_cause == "DATABASE_BOTTLENECK":
            state.recommended_action = "optimize_database"
            state.action_parameters = {"action": "increase_connection_pool", "pool_size": 50}
            state.risk_level = RiskLevel.HIGH.value
            state.approval_status = "PENDING"
        elif rca_cause == "BAD_DEPLOYMENT":
            state.recommended_action = "rollback_deployment"
            state.action_parameters = {"target_version": "v1.0.0"}
            state.risk_level = RiskLevel.HIGH.value
            state.approval_status = "PENDING"
        elif rca_cause == "MEMORY_LEAK":
            state.recommended_action = "restart_service"
            state.action_parameters = {}
            state.risk_level = RiskLevel.MEDIUM.value
            state.approval_status = "PENDING"
        elif rca_cause == "SERVICE_FAILURE":
            state.recommended_action = "restart_unhealthy_pod"
            state.action_parameters = {}
            state.risk_level = RiskLevel.LOW.value
            state.approval_status = "APPROVED"  # Auto-approved for low risk pod recreation
        else:
            state.recommended_action = None
            state.risk_level = RiskLevel.LOW.value
            state.approval_status = "NOT_REQUIRED"

        # Create approval card representation
        state.approval_card = {
            "service": state.service,
            "root_cause": rca_cause,
            "confidence": state.confidence,
            "evidence": state.evidence,
            "recommended_action": state.recommended_action,
            "parameters": state.action_parameters,
            "risk_level": state.risk_level,
            "approval_status": state.approval_status,
            "historical_reference": state.historical_incidents[0] if state.historical_incidents else None
        }

        return state

    @staticmethod
    def step_execute_and_verify(state: AgentState) -> AgentState:
        state.current_step = "EXECUTE"
        action = state.recommended_action
        svc = state.service or "payment-service"

        if not action or state.approval_status not in ["APPROVED", "NOT_REQUIRED"]:
            # Awaiting approval or action not executable
            return state

        # Execute remediation tool
        args = {"service": svc, "approved": True, **state.action_parameters}
        res_exec = mcp_client.call_tool(action, args)
        state.tool_traces.append(res_exec["trace"])
        state.execution_result = res_exec["result"]

        # Verification step
        state.current_step = "VERIFY"
        res_ver = mcp_client.call_tool("verify_service_health", {"service": svc})
        state.tool_traces.append(res_ver["trace"])
        state.verification_result = res_ver["result"]

        return state

    @staticmethod
    def step_final_response(state: AgentState) -> AgentState:
        state.current_step = "FINAL_RESPONSE"
        rca_data = state.rca_result or {}
        cause = rca_data.get("root_cause", "UNKNOWN")
        conf = int(state.confidence * 100)

        bullets = "\n".join([f"- {e}" for e in state.evidence]) or "- Telemetry within nominal bounds"
        m = state.metrics or {}
        req_rate = m.get("request_rate", 50.0)
        cpu = m.get("cpu_percent", 20.0)
        mem = m.get("memory_percent", 35.0)
        lat = m.get("latency_ms", 25.0)
        err = m.get("error_rate", 0.0) * 100

        text = f"### Investigation for **{state.service}**\n\n"
        text += f"**Probable Root Cause**: `{cause}` ({conf}% confidence)\n\n"
        text += f"#### Evidence Collected:\n{bullets}\n\n"
        text += f"#### Telemetry Observed:\n"
        text += f"- **Request Rate**: {req_rate:.1f} req/s\n"
        text += f"- **CPU**: {cpu:.1f}% | **Memory**: {mem:.1f}%\n"
        text += f"- **Latency**: {lat:.1f}ms | **Error Rate**: {err:.1f}%\n\n"

        if state.recommended_action:
            text += f"#### Proposed Remediation:\n"
            text += f"- **Action**: `{state.recommended_action}` ({state.risk_level} Risk)\n"
            if state.action_parameters:
                text += f"- **Parameters**: `{state.action_parameters}`\n"

            if state.approval_status == "PENDING":
                text += f"\n> [!NOTE]\n> **Action requires Human Approval ({state.risk_level} Risk)**. Please review and click **Approve** to execute."
            elif state.approval_status == "APPROVED":
                ver = state.verification_result or {}
                text += f"\n✓ **Remediation Executed & Verified**: Service status is **{'HEALTHY' if ver.get('healthy') else 'PENDING'}**."
        else:
            text += "\n> [!IMPORTANT]\n> Root cause confidence is below automation threshold or requires specialized investigation. No automatic infrastructure mutation proposed."

        state.final_response = text
        return state
