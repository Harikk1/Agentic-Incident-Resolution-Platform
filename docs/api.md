# SmartOps AI REST API Reference

The backend exposes a REST API powered by FastAPI with JWT authentication, role-based access control (RBAC), and correlation ID tracking headers.

## Endpoints

### Authentication & Authorization
- `POST /api/auth/login`: Authenticate with email/password and receive JWT token.
- `GET /api/auth/me`: Inspect authenticated user permissions.

### Services Fleet
- `GET /api/services`: List all registered microservices with real-time status and live metrics.
- `GET /api/services/{service}/metrics`: Get live metrics and historical buffer for a service.
- `GET /api/services/{service}/health`: Run live health verification probes.
- `GET /api/services/{service}/history`: Retrieve time-series telemetry points.

### Incidents Management
- `GET /api/incidents`: Filter incidents by state or list all.
- `POST /api/incidents`: Manually or automatically trigger incident creation.
- `GET /api/incidents/{id}`: Detailed incident view with symptoms, logs, and RCA.
- `POST /api/incidents/{id}/investigate`: Transition to INVESTIGATING and gather telemetry.
- `POST /api/incidents/{id}/diagnose`: Run 12-candidate evidence-based RCA.
- `POST /api/incidents/{id}/approve`: Authorize pending remediation and execute in K8s.
- `POST /api/incidents/{id}/reject`: Reject proposed remediation and escalate to manual review.
- `GET /api/incidents/{id}/timeline`: Retrieve structured audit timeline of state transitions.

### Agentic Conversational AI (Mode B)
- `POST /api/chat`: Conversational query to the SmartOps Agent; returns response, live MCP tool traces, and inline approval card.

### Remediation & Audit
- `GET /api/remediation/{id}`: Inspect execution status of an infrastructure action.
- `GET /api/audit`: Query immutable compliance audit logs.
