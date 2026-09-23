import os
import sys
import httpx
import time

PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://127.0.0.1:8003")
BACKEND_URL = os.getenv("SMARTOPS_BACKEND_URL", "http://127.0.0.1:8000")

def inject_fault(faults: dict, service_url: str = PAYMENT_SERVICE_URL):
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.post(f"{service_url}/api/faults", json=faults)
            if resp.status_code == 200:
                print(f"[SUCCESS] Fault injected: {faults}")
                return True
            else:
                print(f"[ERROR] Failed to inject fault: HTTP {resp.status_code}")
                return False
    except Exception as e:
        print(f"[ERROR] Could not connect to {service_url}: {e}")
        return False

def reset_all_faults(service_url: str = PAYMENT_SERVICE_URL):
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.delete(f"{service_url}/api/faults")
            print(f"[SUCCESS] All faults cleared: {resp.json()}")
            return True
    except (httpx.ConnectError, ConnectionRefusedError):
        print(f"[INFO] Service at {service_url} is offline. Faults are held in-memory and are already cleared.")
        return True
    except Exception as e:
        print(f"[ERROR] Could not clear faults: {e}")
        return False
