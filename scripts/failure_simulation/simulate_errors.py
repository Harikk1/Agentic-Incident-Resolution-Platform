import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import inject_fault

if __name__ == "__main__":
    rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.08
    print(f"Injecting {rate*100}% random HTTP 500 error rate...")
    inject_fault({"error_rate": rate})
