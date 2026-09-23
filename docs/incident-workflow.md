# Incident Lifecycle & State Machine Workflow

SmartOps implements a strict 10-state incident lifecycle state machine. Arbitrary transitions are blocked.

```
DETECTED
   ↓
INVESTIGATING
   ↓
DIAGNOSED ──── (confidence < 0.50) ────→ NEEDS_HUMAN_REVIEW
   ↓
REMEDIATION_PROPOSED
   ↓
WAITING_APPROVAL (for Medium / High Risk)
   ↓
REMEDIATION_EXECUTING
   ↓
VERIFYING
   ↓
RESOLVED (or REMEDIATION_FAILED)
```

## State Machine Invariants
1. Incidents cannot jump directly from `DETECTED` to `RESOLVED` without verification.
2. If root cause confidence is below 50%, state must transition to `NEEDS_HUMAN_REVIEW` rather than guessing a cause.
3. Every mutating remediation action must enter `VERIFYING` and confirm live readiness before reaching `RESOLVED`.
