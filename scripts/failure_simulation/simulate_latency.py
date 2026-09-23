import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import inject_fault

if __name__ == "__main__":
    latency = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    print(f"Injecting {latency}ms artificial latency...")
    inject_fault({"latency_ms": latency})
