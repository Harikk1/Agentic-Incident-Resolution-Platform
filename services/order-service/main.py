import time
import os
import uuid
import psutil
import httpx
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Order Service", version="1.0.0")

SERVICE_NAME = "order-service"
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8001")

# Prometheus Metrics
REQUESTS_TOTAL = Counter("http_requests_total", "Total HTTP Requests", ["service", "method", "endpoint", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP Request Duration in Seconds", ["service", "endpoint"])
ACTIVE_REQUESTS = Gauge("active_requests", "Active HTTP Requests", ["service"])
CPU_USAGE = Gauge("service_cpu_percent", "Service Process CPU Percent", ["service"])
MEMORY_USAGE = Gauge("service_memory_percent", "Service Process Memory Percent", ["service"])
SERVICE_AVAILABILITY = Gauge("service_availability", "Service Availability Status", ["service"])

# Dependency Metrics
DEPENDENCY_DURATION = Histogram("dependency_request_duration_seconds", "Dependency Request Duration", ["service", "dependency"])
DEPENDENCY_FAILURES = Counter("dependency_failures_total", "Dependency Failures Total", ["service", "dependency"])

SERVICE_AVAILABILITY.labels(service=SERVICE_NAME).set(1)

class OrderCreate(BaseModel):
    user_id: str
    items: List[str]
    total_amount: float

ORDERS_DB = {
    "ord-5001": {
        "order_id": "ord-5001",
        "user_id": "usr-1001",
        "items": ["laptop", "mouse"],
        "total_amount": 1250.0,
        "status": "COMPLETED",
        "created_at": time.time() - 3600
    }
}

@app.middleware("http")
async def metrics_middleware(request, call_next):
    endpoint = request.url.path
    if endpoint == "/metrics":
        return await call_next(request)
        
    ACTIVE_REQUESTS.labels(service=SERVICE_NAME).inc()
    start_time = time.time()
    status_code = 500
    try:
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
    return {
        "status": "UP",
        "service": SERVICE_NAME,
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@app.get("/orders")
def list_orders():
    return list(ORDERS_DB.values())

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        
    # Enrich with user details from User Service
    user_info = None
    start_dep = time.time()
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{USER_SERVICE_URL}/users/{order['user_id']}")
            if resp.status_code == 200:
                user_info = resp.json()
    except Exception:
        DEPENDENCY_FAILURES.labels(service=SERVICE_NAME, dependency="user-service").inc()
    finally:
        DEPENDENCY_DURATION.labels(service=SERVICE_NAME, dependency="user-service").observe(time.time() - start_dep)
        
    return {**order, "user_details": user_info}

@app.post("/orders")
async def create_order(payload: OrderCreate):
    # Verify user exists via User Service dependency
    start_dep = time.time()
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{USER_SERVICE_URL}/users/{payload.user_id}")
            if resp.status_code != 200:
                DEPENDENCY_FAILURES.labels(service=SERVICE_NAME, dependency="user-service").inc()
                raise HTTPException(status_code=400, detail=f"User {payload.user_id} does not exist")
    except httpx.RequestError:
        DEPENDENCY_FAILURES.labels(service=SERVICE_NAME, dependency="user-service").inc()
        raise HTTPException(status_code=503, detail="User Service dependency unavailable")
    finally:
        DEPENDENCY_DURATION.labels(service=SERVICE_NAME, dependency="user-service").observe(time.time() - start_dep)
        
    order_id = f"ord-{uuid.uuid4().hex[:6]}"
    order = {
        "order_id": order_id,
        "user_id": payload.user_id,
        "items": payload.items,
        "total_amount": payload.total_amount,
        "status": "CREATED",
        "created_at": time.time()
    }
    ORDERS_DB[order_id] = order
    return order

@app.get("/api/faults")
def get_faults():
    return {
        "latency_ms": 0,
        "error_rate": 0.0,
        "cpu_burn": False,
        "memory_leak": False,
        "db_bottleneck": False,
        "bad_deployment": False,
        "service_failure": False
    }

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
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
