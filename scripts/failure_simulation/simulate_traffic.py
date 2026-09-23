import sys
import os
import time
import httpx
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from scripts.failure_simulation.common import inject_fault, PAYMENT_SERVICE_URL

def blast_traffic(duration_sec: int = 5):
    start = time.time()
    while time.time() - start < duration_sec:
        try:
            with httpx.Client(timeout=1.0) as client:
                client.post(f"{PAYMENT_SERVICE_URL}/payments", json={"order_id": "ord-5001", "amount": 100.0})
        except Exception:
            pass

if __name__ == "__main__":
    print("Activating Traffic Surge simulation (Scenario 1)...")
    inject_fault({"latency_ms": 160, "cpu_burn": True})
    threads = [threading.Thread(target=blast_traffic, args=(6,)) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Traffic spike generation complete.")
