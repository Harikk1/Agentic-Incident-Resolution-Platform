# Model Context Protocol (MCP) Server & Tools

SmartOps implements the official Python Model Context Protocol (`mcp.server.fastmcp.FastMCP`), exposing 25 tools and 5 read-only resource schemas.

## MCP Tools (25)

### 1. Monitoring Tools
- `get_service_metrics(service)`: Retrieves CPU, memory, disk, latency, request rate, and error rate.
- `get_service_health(service)`: Queries pod status and HTTP probes.
- `get_all_services()`: Retrieves full inventory of registered services.
- `get_pod_status(service)`: Details container restart counts and readiness.
- `get_dependency_health(service)`: Queries upstream dependencies.

### 2. Incident Tools
- `get_active_incidents()`: Returns all unresolved incidents.
- `get_incident(incident_id)`: Fetches complete incident object.
- `get_incident_history(service)`: Historical incidents for a service.
- `get_recent_incidents(service)`: Returns last 5 incidents.

### 3. Log Tools
- `search_logs(service, time_range, severity, query)`: Queries structured logs.
- `get_error_summary(service)`: Summarizes 5xx errors and timeouts.
- `get_recent_errors(service)`: Returns recent ERROR-level logs.

### 4. Diagnostic Tools
- `detect_anomaly(service)`: Runs hybrid Threshold + Z-Score/IQR + Isolation Forest ML detection.
- `predict_root_cause(service, incident_id)`: Evaluates 12 root-cause candidates and computes confidence.
- `investigate_incident(service, incident_id)`: Aggregates metrics, logs, dependencies, and anomaly signals.
- `compare_with_baseline(service)`: Computes multipliers against nominal baselines.
- `find_similar_incidents(service, query)`: Vector search over historical incidents (RAG).

### 5. Remediation Tools
- `scale_service(service, replicas)`: Safely scales replicas (1-15).
- `restart_service(service)`: Rolling rollout restart.
- `restart_unhealthy_pod(service)`: Recreates unhealthy container.
- `rollback_deployment(service)`: Restores previous stable revision.
- `increase_resources(service, cpu_request, memory_request)`: Patches resource limits.
- `scale_consumers(service, replicas)`: Scales consumer workers.
- `cleanup_disk(service)`: Cleans volume cache.
- `verify_service_health(service)`: Verifies recovery post-remediation.

## Read-Only Resources
- `service://{service}/health`
- `service://{service}/metrics`
- `service://{service}/logs`
- `service://{service}/incidents`
- `incident://{id}`
