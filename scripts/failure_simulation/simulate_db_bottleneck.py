import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import inject_fault

if __name__ == "__main__":
    print("Activating Database Bottleneck simulation (Scenario 2)...")
    # Injects high DB query latency, connection pool timeouts, and timeout logs while CPU remains normal!
    inject_fault({"db_bottleneck": True, "latency_ms": 260, "cpu_burn": False})
    print("Database bottleneck activated: DB query latency spiked to 380ms with timeout warnings.")
