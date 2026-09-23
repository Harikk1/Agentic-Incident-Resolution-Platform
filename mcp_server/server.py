"""
SmartOps FastMCP Server - Official Python Model Context Protocol implementation.
Exposes controlled Monitoring, Diagnosis, Incident, Log, and Remediation tools and read-only resources.
"""
import os
import json
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
from mcp_server.dependencies.backend_client import bridge

# Initialize FastMCP Server
mcp = FastMCP(
    "SmartOps-Incident-Response-Server",
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", 8005))
)

# ==========================================
# 1. MONITORING TOOLS (Section 21)
# ==========================================

@mcp.tool()
def get_service_metrics(service: str) -> Dict[str, Any]:
    """Retrieve current CPU, memory, latency, request rate, and error rate for a service."""
    return bridge.get_service_metrics(service)

@mcp.tool()
def get_service_health(service: str) -> Dict[str, Any]:
    """Check live health status and readiness probes for a service."""
    return bridge.get_service_health(service)

@mcp.tool()
def get_all_services() -> List[Dict[str, Any]]:
    """Retrieve inventory of all microservices, their status, replicas, and dependency links."""
    return bridge.get_all_services()

@mcp.tool()
def get_pod_status(service: str) -> List[Dict[str, Any]]:
    """Inspect underlying Kubernetes pods, container restart counts, and readiness for a service."""
    return bridge.get_pod_status(service)

@mcp.tool()
def get_dependency_health(service: str) -> List[Dict[str, Any]]:
    """Check health and communication latency for upstream and downstream service dependencies."""
    return bridge.get_dependency_health(service)

# ==========================================
# 2. INCIDENT TOOLS (Section 22)
# ==========================================

@mcp.tool()
def get_active_incidents() -> List[Dict[str, Any]]:
    """Retrieve all currently active, unresolved incidents across the platform."""
    return bridge.get_active_incidents()

@mcp.tool()
def get_incident(incident_id: str) -> Dict[str, Any]:
    """Retrieve complete incident object, current state, symptoms, and timeline events."""
    inc = bridge.get_incident(incident_id)
    if not inc:
        return {"error": f"Incident {incident_id} not found"}
    return inc

@mcp.tool()
def get_incident_history(service: str) -> List[Dict[str, Any]]:
    """Retrieve historical incidents recorded for a specific microservice."""
    return bridge.get_incident_history(service)

@mcp.tool()
def get_recent_incidents(service: str) -> List[Dict[str, Any]]:
    """Retrieve the most recent incidents and resolutions for a service."""
    history = bridge.get_incident_history(service)
    return history[-5:]

# ==========================================
# 3. LOG TOOLS (Section 23)
# ==========================================

@mcp.tool()
def search_logs(service: str, time_range: str = "1h", severity: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search structured application and container logs for exceptions, timeouts, or keywords."""
    return bridge.search_logs(service=service, severity=severity, query=query)

@mcp.tool()
def get_error_summary(service: str) -> Dict[str, Any]:
    """Summarize error logs and count occurrences of timeouts, 5xx codes, and exceptions."""
    logs = bridge.search_logs(service=service, severity="ERROR", limit=50)
    return {
        "service": service,
        "error_count": len(logs),
        "recent_errors": [l.get("message") for l in logs[:5]]
    }

@mcp.tool()
def get_recent_errors(service: str) -> List[Dict[str, Any]]:
    """Retrieve the most recent error-level logs recorded for a microservice."""
    return bridge.search_logs(service=service, severity="ERROR", limit=10)

# ==========================================
# 4. DIAGNOSTIC TOOLS (Section 24)
# ==========================================

@mcp.tool()
def detect_anomaly(service: str) -> Dict[str, Any]:
    """Run hybrid threshold, statistical (Z-Score/IQR), and Isolation Forest ML anomaly detection."""
    return bridge.detect_anomaly(service)

@mcp.tool()
def predict_root_cause(service: str, incident_id: Optional[str] = None) -> Dict[str, Any]:
    """Perform evidence-based root-cause analysis (RCA) evaluating all 12 root cause candidates."""
    return bridge.predict_root_cause(service, incident_id)

@mcp.tool()
def investigate_incident(service: str, incident_id: Optional[str] = None) -> Dict[str, Any]:
    """Comprehensive investigation aggregating metrics, logs, dependencies, and anomaly signals."""
    metrics = bridge.get_service_metrics(service)
    health = bridge.get_service_health(service)
    deps = bridge.get_dependency_health(service)
    errors = bridge.search_logs(service=service, severity="ERROR", limit=5)
    anomaly = bridge.detect_anomaly(service)
    rca = bridge.predict_root_cause(service, incident_id)
    return {
        "service": service,
        "metrics": metrics,
        "health": health,
        "dependencies": deps,
        "recent_errors": errors,
        "anomaly": anomaly,
        "rca": rca
    }

@mcp.tool()
def compare_with_baseline(service: str) -> Dict[str, Any]:
    """Compare current telemetry values against normal baseline operating profiles."""
    return bridge.compare_with_baseline(service)

@mcp.tool()
def find_similar_incidents(service: str, query: str = "") -> List[Dict[str, Any]]:
    """RAG tool: Search vector knowledge base for past incidents matching the symptoms."""
    return bridge.find_similar_incidents(service, query)

# ==========================================
# 5. REMEDIATION TOOLS (Section 25)
# ==========================================

@mcp.tool()
def restart_service(service: str) -> Dict[str, Any]:
    """Safely perform rolling restart of service deployment via Kubernetes API."""
    return bridge.execute_remediation("restart_service", service, {})

@mcp.tool()
def restart_unhealthy_pod(service: str) -> Dict[str, Any]:
    """Safely recreate unhealthy or crashed pod instance via Kubernetes API."""
    return bridge.execute_remediation("restart_pod", service, {})

@mcp.tool()
def scale_service(service: str, replicas: int) -> Dict[str, Any]:
    """Safely scale deployment replicas (between 1 and 15) to absorb traffic surges."""
    return bridge.execute_remediation("scale_service", service, {"replicas": replicas})

@mcp.tool()
def increase_resources(service: str, cpu_request: str = "1000m", memory_request: str = "1Gi") -> Dict[str, Any]:
    """Safely patch deployment CPU and memory request bounds via Kubernetes API."""
    return bridge.execute_remediation("increase_resources", service, {"cpu_request": cpu_request, "memory_request": memory_request})

@mcp.tool()
def rollback_deployment(service: str) -> Dict[str, Any]:
    """Safely rollback deployment to previous known-stable revision following regression release."""
    return bridge.execute_remediation("rollback_deployment", service, {})

@mcp.tool()
def scale_consumers(service: str, replicas: int) -> Dict[str, Any]:
    """Scale queue consumer worker replicas."""
    return bridge.execute_remediation("scale_consumers", service, {"replicas": replicas})

@mcp.tool()
def cleanup_disk(service: str) -> Dict[str, Any]:
    """Clean temporary cache directories and rotate log files on the host/volume."""
    return bridge.execute_remediation("cleanup_disk", service, {})

@mcp.tool()
def verify_service_health(service: str) -> Dict[str, Any]:
    """Verify pod readiness, HTTP health endpoint, and metric stabilization post-remediation."""
    return bridge.get_service_health(service)

# ==========================================
# 6. READ-ONLY MCP RESOURCES (Section 26)
# ==========================================

@mcp.resource("service://{service}/health")
def resource_service_health(service: str) -> str:
    """Read-only resource for service health state."""
    return json.dumps(bridge.get_service_health(service), indent=2)

@mcp.resource("service://{service}/metrics")
def resource_service_metrics(service: str) -> str:
    """Read-only resource for service metrics snapshot."""
    return json.dumps(bridge.get_service_metrics(service), indent=2)

@mcp.resource("service://{service}/logs")
def resource_service_logs(service: str) -> str:
    """Read-only resource for recent service logs."""
    return json.dumps(bridge.search_logs(service=service, limit=20), indent=2)

@mcp.resource("service://{service}/incidents")
def resource_service_incidents(service: str) -> str:
    """Read-only resource for incidents associated with a service."""
    return json.dumps(bridge.get_incident_history(service), indent=2)

@mcp.resource("incident://{incident_id}")
def resource_incident(incident_id: str) -> str:
    """Read-only resource for single incident details and timeline."""
    return json.dumps(bridge.get_incident(incident_id) or {}, indent=2)

from starlette.responses import JSONResponse

@mcp.custom_route("/", methods=["GET"])
async def root_status(request):
    """Informative root page for browser access to FastMCP Server."""
    return JSONResponse({
        "status": "UP",
        "server": "SmartOps FastMCP Server",
        "description": "Model Context Protocol Server providing 25 tools and 5 resources for AIOps Incident Response",
        "transport": "SSE (Server-Sent Events)",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "tools": "/tools",
            "sse_stream": "/sse",
            "messages": "/messages/"
        },
        "tools_count": 25,
        "resources_count": 5
    })

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for container orchestrators and monitoring probes."""
    return JSONResponse({
        "status": "UP",
        "service": "fastmcp-server",
        "port": 8005,
        "healthy": True
    })

@mcp.custom_route("/tools", methods=["GET"])
async def list_registered_tools(request):
    """List all registered MCP tools and descriptions."""
    tools_list = []
    for tool in mcp._tool_manager.list_tools():
        tools_list.append({
            "name": tool.name,
            "description": tool.description
        })
    return JSONResponse({
        "total_tools": len(tools_list),
        "tools": tools_list
    })

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "sse")
    mcp.run(transport=transport)
