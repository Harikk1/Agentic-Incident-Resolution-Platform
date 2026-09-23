import time
import os
import uuid
import psutil
import httpx
import random
import threading
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Response, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Payment Service", version="1.0.0")

SERVICE_NAME = "payment-service"
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://127.0.0.1:8002")

# Prometheus Metrics
REQUESTS_TOTAL = Counter("http_requests_total", "Total HTTP Requests", ["service", "method", "endpoint", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP Request Duration in Seconds", ["service", "endpoint"])
ACTIVE_REQUESTS = Gauge("active_requests", "Active HTTP Requests", ["service"])
CPU_USAGE = Gauge("service_cpu_percent", "Service Process CPU Percent", ["service"])
MEMORY_USAGE = Gauge("service_memory_percent", "Service Process Memory Percent", ["service"])
SERVICE_AVAILABILITY = Gauge("service_availability", "Service Availability Status", ["service"])

# Specific Payment & Database Metrics
DATABASE_LATENCY = Histogram("database_query_duration_seconds", "Database Query Latency", ["service", "operation"])
DATABASE_TIMEOUTS = Counter("database_timeouts_total", "Database Timeout Errors", ["service"])
DEPENDENCY_DURATION = Histogram("dependency_request_duration_seconds", "Dependency Duration", ["service", "dependency"])
DEPENDENCY_FAILURES = Counter("dependency_failures_total", "Dependency Failures", ["service", "dependency"])

SERVICE_AVAILABILITY.labels(service=SERVICE_NAME).set(1)

# In-memory storage and log history
PAYMENTS_DB: Dict[str, Any] = {
    "pay-9001": {
        "payment_id": "pay-9001",
        "order_id": "ord-5001",
        "amount": 1250.0,
        "status": "SUCCESS",
        "created_at": time.time() - 1800
    }
}

SERVICE_LOGS: List[Dict[str, Any]] = [
    {
        "timestamp": time.time() - 3600,
        "service": SERVICE_NAME,
        "level": "INFO",
        "message": "Payment service initialized successfully"
    }
]

# Fault Injection State
FAULT_STATE = {
    "latency_ms": 0,
    "error_rate": 0.0,
    "cpu_burn": False,
    "memory_leak": False,
    "db_bottleneck": False,
    "service_failure": False,
    "bad_deployment": False,
    "version": "v1.0.0"
}

_memory_leaker: List[bytes] = []
_cpu_burning = False

def cpu_worker():
    global _cpu_burning
    while _cpu_burning:
        _ = [x**2 for x in range(10000)]
        time.sleep(0.001)

def add_log(level: str, message: str, **kwargs):
    entry = {
        "timestamp": time.time(),
        "service": SERVICE_NAME,
        "level": level,
        "message": message,
        **kwargs
    }
    SERVICE_LOGS.append(entry)
    if len(SERVICE_LOGS) > 1000:
        SERVICE_LOGS.pop(0)

class PaymentCreate(BaseModel):
    order_id: str
    amount: float
    payment_method: str = "CREDIT_CARD"

@app.middleware("http")
async def metrics_middleware(request, call_next):
    endpoint = request.url.path
    if endpoint == "/metrics":
        return await call_next(request)
        
    ACTIVE_REQUESTS.labels(service=SERVICE_NAME).inc()
    start_time = time.time()
    status_code = 500
    
    try:
        # Check simulated service failure
        if FAULT_STATE["service_failure"] and endpoint != "/api/faults":
            SERVICE_AVAILABILITY.labels(service=SERVICE_NAME).set(0)
            add_log("ERROR", "Service health check failed: internal process unresponsive")
            status_code = 503
            return JSONResponse(status_code=503, content={"detail": "Service Unavailable: Crashed or Unhealthy"})
        else:
            SERVICE_AVAILABILITY.labels(service=SERVICE_NAME).set(1)

        # Injected latency
        if FAULT_STATE["latency_ms"] > 0:
            time.sleep(FAULT_STATE["latency_ms"] / 1000.0)

        # Injected error rate
        if FAULT_STATE["error_rate"] > 0 and random.random() < FAULT_STATE["error_rate"]:
            add_log("ERROR", f"Random injected failure triggered: HTTP 500 on {endpoint}")
            status_code = 500
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error: Injected Error Rate"})

        # Bad deployment behavior
        if FAULT_STATE["bad_deployment"] and endpoint != "/api/faults":
            if random.random() < 0.65:
                add_log("ERROR", "NullPointerException in com.smartops.payment.Processor.execute(): Bad deployment release v2.1.0-bad")
                status_code = 500
                return JSONResponse(status_code=500, content={"detail": "Deployment regression failure in v2.1.0-bad"})

        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration = time.time() - start_time
        ACTIVE_REQUESTS.labels(service=SERVICE_NAME).dec()
        REQUESTS_TOTAL.labels(service=SERVICE_NAME, method=request.method, endpoint=endpoint, status=str(status_code)).inc()
        REQUEST_DURATION.labels(service=SERVICE_NAME, endpoint=endpoint).observe(duration)
        try:
            CPU_USAGE.labels(service=SERVICE_NAME).set(psutil.cpu_percent())
            MEMORY_USAGE.labels(service=SERVICE_NAME).set(psutil.virtual_memory().percent)
        except Exception:
            pass

@app.get("/health")
def health():
    if FAULT_STATE["service_failure"]:
        raise HTTPException(status_code=503, detail="Unhealthy")
    return {
        "status": "UP",
        "service": SERVICE_NAME,
        "timestamp": time.time(),
        "version": FAULT_STATE["version"],
        "faults_active": {k: v for k, v in FAULT_STATE.items() if v}
    }

@app.post("/payments")
async def create_payment(payload: PaymentCreate):
    # Dependency Check: Order Service
    start_dep = time.time()
    order_data = None
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{ORDER_SERVICE_URL}/orders/{payload.order_id}")
            if resp.status_code == 200:
                order_data = resp.json()
            elif resp.status_code == 404:
                raise HTTPException(status_code=400, detail=f"Order {payload.order_id} not found")
    except httpx.RequestError:
        DEPENDENCY_FAILURES.labels(service=SERVICE_NAME, dependency="order-service").inc()
        add_log("ERROR", f"Dependency failure calling Order Service at {ORDER_SERVICE_URL}")
        # Proceed or raise based on availability
    finally:
        DEPENDENCY_DURATION.labels(service=SERVICE_NAME, dependency="order-service").observe(time.time() - start_dep)

    # Simulated DB query latency & bottleneck
    db_start = time.time()
    if FAULT_STATE["db_bottleneck"]:
        time.sleep(0.35)  # 350ms DB query
        DATABASE_TIMEOUTS.labels(service=SERVICE_NAME).inc()
        add_log("WARN", "Database connection pool exhausted: query timeout after 350ms on table `transactions`")
    else:
        time.sleep(0.01)  # Normal 10ms DB query
    DATABASE_LATENCY.labels(service=SERVICE_NAME, operation="SELECT_TRANSACTION").observe(time.time() - db_start)

    payment_id = f"pay-{uuid.uuid4().hex[:6]}"
    payment = {
        "payment_id": payment_id,
        "order_id": payload.order_id,
        "amount": payload.amount,
        "payment_method": payload.payment_method,
        "status": "SUCCESS",
        "created_at": time.time()
    }
    PAYMENTS_DB[payment_id] = payment
    add_log("INFO", f"Payment {payment_id} processed successfully for order {payload.order_id}")
    return payment

@app.get("/payments/{payment_id}")
def get_payment(payment_id: str):
    p = PAYMENTS_DB.get(payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")
    return p

# Fault Injection Management API
@app.get("/api/faults")
def get_faults():
    return FAULT_STATE

@app.post("/api/faults")
def set_faults(faults: Dict[str, Any] = Body(...)):
    global _cpu_burning, _memory_leaker
    for k, v in faults.items():
        if k in FAULT_STATE:
            FAULT_STATE[k] = v
            
    # Handle CPU burn
    if FAULT_STATE.get("cpu_burn") and not _cpu_burning:
        _cpu_burning = True
        threading.Thread(target=cpu_worker, daemon=True).start()
        add_log("WARN", "High CPU workload simulation activated")
    elif not FAULT_STATE.get("cpu_burn") and _cpu_burning:
        _cpu_burning = False

    # Handle Memory Leak
    if FAULT_STATE.get("memory_leak"):
        # Allocate 50MB
        _memory_leaker.append(b"M" * (50 * 1024 * 1024))
        add_log("WARN", f"Simulated memory leak: allocated 50MB buffer (total blocks: {len(_memory_leaker)})")
    elif not FAULT_STATE.get("memory_leak") and _memory_leaker:
        _memory_leaker.clear()
        add_log("INFO", "Memory leak buffers cleared following remediation restart")

    # Handle Bad Deployment
    if FAULT_STATE.get("bad_deployment"):
        FAULT_STATE["version"] = "v2.1.0-bad"
        add_log("CRITICAL", "New version deployed: v2.1.0-bad with breaking schema changes")
        
    return {"message": "Fault state updated", "current_state": FAULT_STATE}

@app.delete("/api/faults")
def clear_faults():
    global _cpu_burning, _memory_leaker
    _cpu_burning = False
    _memory_leaker.clear()
    for k in FAULT_STATE:
        if isinstance(FAULT_STATE[k], bool):
            FAULT_STATE[k] = False
        elif isinstance(FAULT_STATE[k], (int, float)):
            FAULT_STATE[k] = 0
    FAULT_STATE["version"] = "v1.0.0"
    SERVICE_AVAILABILITY.labels(service=SERVICE_NAME).set(1)
    add_log("INFO", "All fault injections cleared. Restored normal operations.")
    return {"message": "All faults cleared", "current_state": FAULT_STATE}

@app.get("/api/logs")
def get_logs(limit: int = 50, level: Optional[str] = None):
    logs = SERVICE_LOGS
    if level:
        logs = [log for log in logs if log.get("level") == level.upper()]
    return logs[-limit:]

@app.get("/metrics")
def metrics():
    try:
        CPU_USAGE.labels(service=SERVICE_NAME).set(psutil.cpu_percent())
        MEMORY_USAGE.labels(service=SERVICE_NAME).set(psutil.virtual_memory().percent)
    except Exception:
        pass
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
