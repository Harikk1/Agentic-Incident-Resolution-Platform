import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import inject_fault

if __name__ == "__main__":
    print("Activating Disk Pressure threshold simulation...")
    inject_fault({"disk_pressure": True, "disk_percent": 94.0})
