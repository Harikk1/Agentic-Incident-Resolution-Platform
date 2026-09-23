import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import inject_fault

if __name__ == "__main__":
    print("Activating Bad Deployment regression failure simulation (Scenario 3)...")
    inject_fault({
        "bad_deployment": True,
        "version": "v2.1.0-bad",
        "error_rate": 0.085
    })
    print("Simulated rollout of build v2.1.0-bad with 8.5% 5xx error rate and NullPointerExceptions.")
