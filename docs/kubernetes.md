# Kubernetes Driver & Infrastructure Architecture

SmartOps does not treat MCP as a replacement for Kubernetes. MCP provides the standardized tool interface to the AI Agent, while SmartOps interacts with Kubernetes through the official `kubernetes` Python SDK or the high-fidelity `MockKubernetesDriver`.

```
AI Agent -> MCP Client -> MCP Server -> SmartOps Remediation -> Kubernetes Driver -> Kubernetes API / Cluster
```

## Dual Driver Implementation

1. **`RealKubernetesDriver`**:
   - Integrates with the official `kubernetes` Python SDK (`AppsV1Api`, `CoreV1Api`).
   - Uses in-cluster config or `~/.kube/config`.
   - Executes patch scale deployments, rollout restarts, pod deletion/recreations, and resource requests/limits updates.

2. **`MockKubernetesDriver`**:
   - High-fidelity in-memory simulator activated via `MOCK_KUBERNETES=true`.
   - Simulates deployments, desired vs ready replicas, pods, restart counts, version rollout history, and resource allocations.
   - Enables complete end-to-end local testing and demo without requiring an active Kind/Minikube cluster.
