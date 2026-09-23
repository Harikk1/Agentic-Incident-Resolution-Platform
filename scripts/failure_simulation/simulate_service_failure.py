import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import inject_fault

if __name__ == "__main__":
    print("Activating Service Crash / Unresponsive Health simulation...")
    inject_fault({"service_failure": True})
