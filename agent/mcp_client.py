import time
from typing import Dict, Any, List, Optional
from mcp_server.dependencies.backend_client import bridge
from agent.state import ToolExecutionTrace

class MCPClientBridge:
    """Client layer executing MCP tools and recording execution traces for the AI Agent"""

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        status = "COMPLETED"
        summary = ""
        result = {}

        try:
            if tool_name == "get_service_metrics":
                result = bridge.get_service_metrics(arguments["service"])
                m = result.get("cpu_percent", 0)
                summary = f"Retrieved metrics: CPU={m}%, Latency={result.get('latency_ms', 0)}ms"

            elif tool_name == "get_service_health":
                result = bridge.get_service_health(arguments["service"])
                summary = f"Health check: {'UP' if result.get('healthy') else 'DOWN'} (HTTP {result.get('http_status')})"

            elif tool_name == "get_all_services":
                result = bridge.get_all_services()
                summary = f"Retrieved {len(result)} registered services"

            elif tool_name == "get_dependency_health":
                result = bridge.get_dependency_health(arguments["service"])
                summary = f"Checked {len(result)} upstream dependencies"

            elif tool_name == "get_pod_status":
                result = bridge.get_pod_status(arguments["service"])
                summary = f"Inspected {len(result)} Kubernetes pods"

            elif tool_name == "search_logs":
                result = bridge.search_logs(
                    service=arguments["service"],
                    severity=arguments.get("severity"),
                    query=arguments.get("query")
                )
                summary = f"Found {len(result)} matching log entries"

            elif tool_name == "get_recent_errors":
                result = bridge.search_logs(service=arguments["service"], severity="ERROR", limit=5)
                summary = f"Retrieved {len(result)} recent error records"

            elif tool_name == "detect_anomaly":
                result = bridge.detect_anomaly(arguments["service"])
                summary = f"Anomaly: {result.get('is_anomalous')} ({result.get('severity')})"

            elif tool_name == "predict_root_cause":
                result = bridge.predict_root_cause(arguments["service"], arguments.get("incident_id"))
                summary = f"RCA: {result.get('root_cause')} ({int(result.get('confidence', 0)*100)}%)"

            elif tool_name == "compare_with_baseline":
                result = bridge.compare_with_baseline(arguments["service"])
                summary = "Baseline deviations calculated"

            elif tool_name == "find_similar_incidents":
                result = bridge.find_similar_incidents(arguments["service"], arguments.get("query", ""))
                summary = f"Found {len(result)} similar historical incidents"

            elif tool_name in ["scale_service", "restart_service", "restart_unhealthy_pod", "rollback_deployment", "increase_resources", "cleanup_disk"]:
                result = bridge.execute_remediation(
                    action=tool_name,
                    service=arguments["service"],
                    parameters=arguments,
                    actor="AI_AGENT",
                    approved=arguments.get("approved", True)
                )
                summary = f"Remediation {tool_name} executed: {result.get('status')}"

            elif tool_name == "verify_service_health":
                result = bridge.get_service_health(arguments["service"])
                summary = f"Post-remediation verification: {'HEALTHY' if result.get('healthy') else 'UNHEALTHY'}"

            else:
                status = "FAILED"
                summary = f"Unknown MCP tool '{tool_name}'"
                result = {"error": summary}

        except Exception as e:
            status = "FAILED"
            summary = f"Error executing {tool_name}: {str(e)}"
            result = {"error": str(e)}

        trace = ToolExecutionTrace(
            tool_name=tool_name,
            arguments=arguments,
            status=status,
            result_summary=summary,
            timestamp=start
        )
        return {"result": result, "trace": trace}

mcp_client = MCPClientBridge()
