import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import inject_fault

if __name__ == "__main__":
    print("Activating Queue Backlog / Active Requests Saturation simulation...")
    inject_fault({"active_requests": 85, "latency_ms": 190})
