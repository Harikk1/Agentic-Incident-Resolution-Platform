import time
import os
import psutil
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="User Service", version="1.0.0")

# Prometheus Metrics
REQUESTS_TOTAL = Counter("http_requests_total", "Total HTTP Requests", ["service", "method", "endpoint", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP Request Duration in Seconds", ["service", "endpoint"])
ACTIVE_REQUESTS = Gauge("active_requests", "Active HTTP Requests", ["service"])
CPU_USAGE = Gauge("service_cpu_percent", "Service Process CPU Percent", ["service"])
MEMORY_USAGE = Gauge("service_memory_percent", "Service Process Memory Percent", ["service"])
SERVICE_AVAILABILITY = Gauge("service_availability", "Service Availability Status (1=Up, 0=Down)", ["service"])

# In-memory users store
USERS_DB = {
    "usr-1001": {"id": "usr-1001", "name": "Alice Johnson", "email": "alice@example.com", "role": "ENGINEER"},
    "usr-1002": {"id": "usr-1002", "name": "Bob Smith", "email": "bob@example.com", "role": "ADMIN"},
    "usr-1003": {"id": "usr-1003", "name": "Charlie Brown", "email": "charlie@example.com", "role": "VIEWER"}
}

SERVICE_NAME = "user-service"
SERVICE_AVAILABILITY.labels(service=SERVICE_NAME).set(1)

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

@app.get("/users/{user_id}")
def get_user(user_id: str):
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user

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
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
