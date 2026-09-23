# SmartOps AI Interactive Demonstration Guide

This guide walks through the four major portfolio demonstration scenarios.

---

## Scenario 1: Traffic Surge Scaling

### 1. Trigger Failure Simulation
```bash
python scripts/failure_simulation/simulate_traffic.py
```
- Request rate increases to ~720 req/s.
- CPU increases to ~89%.
- Latency increases to ~185ms.
- Database query latency remains healthy (< 30ms).

### 2. Conversational Agent Investigation
Ask the AI Assistant:
> *"Payment service is slow. Find the cause and fix it."*

### 3. Agent Execution & RCA
- Agent queries `get_service_metrics`, `get_service_health`, `get_dependency_health`, `search_logs`.
- Anomaly Engine reports critical threshold violation on request rate and CPU.
- RCA Engine diagnoses: **`TRAFFIC_SPIKE`** (89% confidence).
- Evidence: *"Request rate increased significantly above baseline; CPU utilization corresponds to high traffic; Database remains normal."*
- Agent proposes: **`scale_service(service="payment-service", replicas=5)`** (MEDIUM Risk).
- Click **Approve & Execute in K8s**.
- Agent executes via MCP $\to$ Kubernetes driver scales deployment $\to$ Post-remediation health verified.

---

## Scenario 2: Database Bottleneck (Contextual Diagnosis)

### 1. Trigger Failure Simulation
```bash
python scripts/failure_simulation/simulate_db_bottleneck.py
```
- Latency spikes to ~280ms.
- Database query latency spikes to ~380ms.
- Logs capture timeout errors: *"Database connection pool exhausted"*.
- **CPU remains normal (~32%)!**

### 2. Conversational Agent Investigation
Ask the AI Assistant:
> *"Payment service is slow. Investigate the cause."*

### 3. Contextual Differentiation
The Agent investigates:
- **API Latency**: Elevated (280ms).
- **CPU**: Normal (32%).
- **Database Latency**: 380ms.
- **Logs**: Connection pool timeouts detected.
- RCA Engine diagnoses: **`DATABASE_BOTTLENECK`** (91% confidence).
- **Key Differentiator**: The agent does **NOT** blindly propose scaling application pods. Instead, it proposes database connection pool optimization and query index review!

---

## Scenario 3: Bad Deployment Regression Rollback

### 1. Trigger Failure Simulation
```bash
python scripts/failure_simulation/simulate_bad_deployment.py
```
- Build revision set to `v2.1.0-bad`.
- Error rate jumps to ~8.5%.
- Logs capture `NullPointerException` stack traces.

### 2. Conversational Agent Investigation
Ask the AI Assistant:
> *"Payment started failing after the latest deployment."*

### 3. Agent Execution & Rollback
- Agent inspects deployment version: `v2.1.0-bad`.
- Logs reveal unhandled runtime exceptions.
- RCA Engine diagnoses: **`BAD_DEPLOYMENT`** (88% confidence).
- Agent proposes: **`rollback_deployment(service="payment-service")`** (HIGH Risk).
- Authorize rollback in the UI.
- Kubernetes driver rolls back to `v1.0.0` $\to$ Error rate drops back to 0.0%.

---

## Scenario 4: Memory Leak Analysis

### 1. Trigger Failure Simulation
```bash
python scripts/failure_simulation/simulate_memory.py
```
- Memory continuously allocates buffers to 94%.

### 2. Conversational Agent Investigation
Ask the AI Assistant:
> *"Check whether Payment has a memory leak."*

### 3. Agent Execution
- Agent queries memory trend buffer and container restart history.
- Returns evidence-backed analysis: **`MEMORY_LEAK`** detected.
- Proposes pod restart and memory trend monitoring.

---

## Restoring Normal Baseline
```bash
python scripts/failure_simulation/clear_faults.py
```
Clears all fault states and returns all services to nominal baseline.
