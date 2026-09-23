# SmartOps AI — MCP-Powered Agentic Incident Response Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Official%20Python%20SDK-purple.svg)](https://modelcontextprotocol.io/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Client%20%26%20Mock-326ce5.svg)](https://kubernetes.io/)
[![Tests](https://img.shields.io/badge/Tests-35%20Passing-brightgreen.svg)]()

> **SmartOps AI** is an autonomous, agentic AIOps platform for microservice telemetry monitoring, multi-layer anomaly detection, evidence-based root cause analysis (RCA), and safe Kubernetes remediation powered by the official **Model Context Protocol (MCP)**.

---

## Architecture Overview

```mermaid
graph TD
    User([SRE / Platform Engineer]) <--> UI[React Dashboard & AI Assistant]
    UI <--> API[FastAPI Gateway :8000]
    API <--> ModeA[SmartOps Deterministic AIOps Engine]
    API <--> Agent[Agentic AI Layer - LangGraph]
    
    Agent <--> MCPClient[MCP Client Bridge]
    MCPClient <--> MCPServer[Official FastMCP Server :8005]
    MCPServer <--> ServiceLayer[Shared SmartOps Service Layer]
    ModeA <--> ServiceLayer

    ServiceLayer --> AnomalyEngine[Anomaly Detection: Threshold + Stats + Isolation Forest]
    ServiceLayer --> RCAEngine[Evidence-Based RCA Engine]
    ServiceLayer --> RemEngine[Safe Parameter-Bounded Remediation]
    ServiceLayer --> RAGEngine[Incident RAG Knowledge Base]

    ServiceLayer --> Mongo[(MongoDB / In-Memory Store)]
    RemEngine --> K8sDriver[Kubernetes Driver: Real API / Mock Driver]
    K8sDriver --> K8sCluster[Kubernetes Cluster / Pods]

    subgraph Microservices Fleet
        UserService[User Service :8001]
        OrderService[Order Service :8002]
        PaymentService[Payment Service :8003]
        OrderService --> UserService
        PaymentService --> OrderService
    end

    ServiceLayer -. Telemetry Scrape .-> Microservices Fleet
```

---

## Key Differentiators: Mode A vs Mode B

| Feature | Mode A: Automated AIOps | Mode B: Agentic AI + MCP |
| :--- | :--- | :--- |
| **Trigger** | Continuous background telemetry polling | Natural language SRE request or incident alert |
| **Investigation** | Rule & metric threshold evaluations | Multi-vector context gathering via 25 MCP tools |
| **RCA** | Heuristic rules matching | Evidence-based reasoning + historical incident RAG |
| **Remediation** | Predefined safe automated policy | Contextual remediation selection with approval guardrails |
| **Human Gate** | Automatic execution for safe policies | Human-in-the-loop approval cards for Medium & High risk |
| **Execution** | Direct SmartOps Service Layer | MCP Remediation Tool $\to$ Kubernetes Driver |
| **Post-Check** | Health check probe | Multi-step readiness, latency drop & error drop verification |

---

## Technology Stack

- **Backend**: Python 3.12+, FastAPI, Pydantic v2, Uvicorn, PyJWT
- **Agentic AI & Protocol**: Official Python MCP SDK (`mcp.server.fastmcp.FastMCP`), LangGraph State Machine, Vector RAG Search
- **Machine Learning & Stats**: scikit-learn (`IsolationForest`), NumPy, SciPy (Z-score, IQR, rolling statistics)
- **Observability**: Prometheus (`prometheus_client`), Grafana Dashboards, Structured JSON Logging with correlation IDs (`request_id`, `incident_id`, `session_id`)
- **Persistence**: MongoDB (`pymongo`) with automatic In-Memory repository fallback for zero-dependency local runs
- **Infrastructure**: Kubernetes Python Client (`AppsV1Api`, `CoreV1Api`), high-fidelity `MockKubernetesDriver`, Docker Compose, Kind/Minikube manifests
- **Frontend**: React 18, Vite, Lucide Icons, Glassmorphic Dark UI Theme

---

## 25 MCP Tools Reference

```text
Monitoring:
  • get_service_metrics(service)
  • get_service_health(service)
  • get_all_services()
  • get_pod_status(service)
  • get_dependency_health(service)

Incidents:
  • get_active_incidents()
  • get_incident(incident_id)
  • get_incident_history(service)
  • get_recent_incidents(service)

Logs:
  • search_logs(service, time_range, severity, query)
  • get_error_summary(service)
  • get_recent_errors(service)

Diagnostics:
  • detect_anomaly(service)
  • predict_root_cause(service, incident_id)
  • investigate_incident(service, incident_id)
  • compare_with_baseline(service)
  • find_similar_incidents(service, query)

Remediation:
  • restart_service(service)
  • restart_unhealthy_pod(service)
  • scale_service(service, replicas)
  • increase_resources(service, cpu_request, memory_request)
  • rollback_deployment(service)
  • scale_consumers(service, replicas)
  • cleanup_disk(service)
  • verify_service_health(service)
```

---

## Quickstart: Running Locally

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-username/smartops_ai_mcp1.git
cd smartops_ai_mcp1

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Run Test Suite (35 Tests)
```bash
pytest -v backend/tests
```

### 3. Run Services Locally
```bash
# Terminal 1: User Service
python -m uvicorn services.user-service.main:app --port 8001

# Terminal 2: Order Service
python -m uvicorn services.order-service.main:app --port 8002

# Terminal 3: Payment Service
python -m uvicorn services.payment-service.main:app --port 8003

# Terminal 4: SmartOps Backend Gateway
python -m uvicorn backend.app.main:app --port 8000

# Terminal 5: FastMCP Server
python -m mcp_server.server

# Terminal 6: React Dashboard
cd frontend && npm install && npm run dev
```

The React Dashboard will be available at **`http://localhost:3000`**.

---

## Running with Docker Compose

To start the full stack including Prometheus, Grafana, MongoDB, backend, MCP server, and frontend:
```bash
docker-compose up --build
```
- React Dashboard: `http://localhost:3000`
- SmartOps API: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (admin / admin)
- FastMCP Server: `http://localhost:8005`

---

## Demonstration Scenarios

### Scenario 1: Traffic Surge Scaling
1. Trigger traffic spike:
   ```bash
   python scripts/failure_simulation/simulate_traffic.py
   ```
2. In AI Assistant, ask: *"Payment service is slow. Find the cause and fix it."*
3. Agent diagnoses `TRAFFIC_SPIKE`, shows evidence, and proposes scaling from 2 to 5 replicas.
4. Click **Approve** to execute via MCP and verify latency reduction.

### Scenario 2: Database Bottleneck (Contextual Differentiation)
1. Trigger DB bottleneck:
   ```bash
   python scripts/failure_simulation/simulate_db_bottleneck.py
   ```
2. Ask AI Assistant: *"Payment service is slow. Investigate."*
3. Agent inspects DB query latency (380ms) and DB timeout logs while CPU remains normal (32%).
4. Diagnoses `DATABASE_BOTTLENECK` and recommends connection pool tuning — **refusing to blindly scale application pods**.

### Scenario 3: Bad Deployment Rollback
1. Trigger bad deployment:
   ```bash
   python scripts/failure_simulation/simulate_bad_deployment.py
   ```
2. Ask AI Assistant: *"Payment started failing after the latest deployment."*
3. Agent inspects `v2.1.0-bad` and NullPointer exceptions, proposes `rollback_deployment`, and restores `v1.0.0` upon approval.

### Scenario 4: Memory Leak Analysis
1. Trigger memory leak:
   ```bash
   python scripts/failure_simulation/simulate_memory.py
   ```
2. Ask AI Assistant: *"Check whether Payment has a memory leak."*
3. Agent evaluates historical memory trend buffer, confirms memory ceiling at 94%, and recommends restart + continued trend observation.

### Restore Baseline
```bash
python scripts/failure_simulation/clear_faults.py
```

---

## Documentation Index

- [Architecture Guide](docs/architecture.md)
- [REST API Reference](docs/api.md)
- [MCP Tools & Resources](docs/mcp.md)
- [AI Agent State Machine](docs/agent.md)
- [Kubernetes Driver Guide](docs/kubernetes.md)
- [Monitoring & Observability](docs/monitoring.md)
- [Incident State Machine](docs/incident-workflow.md)
- [Security & RBAC](docs/security.md)
- [Testing & Verification](docs/testing.md)
- [Interactive Demonstration Guide](docs/demo.md)
