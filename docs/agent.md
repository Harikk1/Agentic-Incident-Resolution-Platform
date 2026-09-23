# AI Agent Workflow (Mode B)

The SmartOps AI Agent implements a 10-step state machine workflow built on LangGraph concepts and official Model Context Protocol (MCP) clients.

## State Machine Workflow

```
UNDERSTAND_REQUEST
        ↓
IDENTIFY_SERVICE
        ↓
COLLECT_CONTEXT (Calls get_service_metrics, get_service_health, get_dependency_health, get_recent_errors)
        ↓
ANALYZE (Calls detect_anomaly, compare_with_baseline)
        ↓
DIAGNOSE (Calls predict_root_cause, find_similar_incidents)
        ↓
PLAN_REMEDIATION (Assigns action, parameters, and risk level)
        ↓
REQUEST_APPROVAL (If MEDIUM or HIGH risk, pauses with approval card)
        ↓
EXECUTE (Calls safe MCP remediation tool upon human authorization)
        ↓
VERIFY (Calls verify_service_health post-remediation)
        ↓
FINAL_RESPONSE (Natural language explanation with evidence and facts)
```

## Contextual Reasoning Differentiator

The agent investigates rather than blindly mapping single metrics:
- **Scenario 1 (Traffic Spike)**: High request rate + elevated CPU + normal DB latency $\to$ Scale payment-service.
- **Scenario 2 (Database Bottleneck)**: High API latency + elevated DB query duration + DB timeout logs + normal CPU $\to$ Recommends database connection pool tuning, avoiding erroneous application pod scaling.
- **Scenario 3 (Bad Deployment)**: Rollout of `v2.1.0-bad` + 5xx error jump + NullPointer exceptions $\to$ Proposes rollback to `v1.0.0`.
- **Scenario 4 (Memory Leak)**: Memory continually increasing to 94% + restart count increasing $\to$ Proposes pod restart and continued memory slope observation.
