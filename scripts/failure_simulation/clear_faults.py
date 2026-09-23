import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import reset_all_faults

if __name__ == "__main__":
    print("Clearing all injected faults and restoring normal operating baseline...")
    reset_all_faults()
