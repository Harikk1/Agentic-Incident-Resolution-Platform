# SmartOps AI Architecture Documentation

SmartOps AI is an MCP-Powered Agentic Incident Response and AIOps platform built from scratch for microservice and Kubernetes environments.

```
React Dashboard (Vite / React 18 / Lucide Icons)
       ↓
FastAPI Backend Gateway (:8000)
       ↓
SmartOps Core Engine & Repositories (MongoDB / In-Memory Fallback)
       ↓
AI Agent / LangGraph Workflow (Mode B)
       ↓
MCP Client Bridge
       ↓
Official FastMCP Server (:8005)
       ↓
25 MCP Tools (Monitoring, Logs, Incidents, Diagnosis, Remediation)
       ↓
SmartOps Shared Service Layer
       ↓
Kubernetes Driver (Real K8s API / Mock K8s Driver)
       ↓
Microservices Fleet (User :8001, Order :8002, Payment :8003)
```

## Two Operating Modes

### Mode A: Deterministic Automated AIOps
Continuous telemetry collection via Prometheus $\to$ Hybrid Anomaly Detection $\to$ Incident Management $\to$ Evidence-based RCA $\to$ Policy Engine $\to$ Safe Kubernetes Execution $\to$ Verification.

### Mode B: Agentic AI + MCP with Human-in-the-Loop
Natural language request $\to$ AI Agent State Machine $\to$ Dynamic MCP Tool Calling $\to$ Multi-vector Context & RCA $\to$ Risk-tiered Approval Guardrails $\to$ MCP Remediation Tool $\to$ Kubernetes API $\to$ Telemetry Verification $\to$ Immutable Audit Trail.
