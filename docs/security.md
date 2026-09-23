# Security, RBAC & Safety Guardrails

SmartOps enforces enterprise-grade security boundaries to prevent unauthorized mutations or destructive actions by autonomous agents.

## Role-Based Access Control (RBAC)
- **`VIEWER`**: Read-only access to services, metrics, incidents, logs, and audit records.
- **`ENGINEER`**: All Viewer permissions + investigate, diagnose, chat with agent, and authorize `MEDIUM` risk remediations (e.g. restart service, scale service).
- **`ADMIN`**: All Engineer permissions + authorize `HIGH` risk remediations (e.g. rollback deployment, resource changes) and configuration management.

## Strict Safety Guardrails
1. **No Arbitrary Shell Execution**: The agent cannot call `bash`, `sh`, or raw commands.
2. **No Arbitrary Kubectl**: The agent cannot execute raw `kubectl` command strings. All mutations pass through typed, parameter-bounded SmartOps remediation functions.
3. **Bound Parameters**: Service names are checked against `ALLOWED_SERVICES`. Replica counts are restricted between 1 and 15.
4. **Immutable Audit Trail**: Every mutating tool execution records actor, timestamp, parameters, risk level, human approval, and result into an append-only audit repository.
