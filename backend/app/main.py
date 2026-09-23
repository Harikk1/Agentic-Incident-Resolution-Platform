import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Gauge

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.middleware import CorrelationIdMiddleware
from backend.app.monitoring.collector import collector

from backend.app.api.auth import router as auth_router
from backend.app.api.services import router as services_router
from backend.app.api.incidents import router as incidents_router
from backend.app.api.remediation import router as remediation_router
from backend.app.api.audit import router as audit_router
from backend.app.api.chat import router as chat_router

# Platform Observability Metrics (Section 58)
AGENT_REQUESTS = Counter("smartops_agent_requests_total", "Total AI agent requests received")
MCP_TOOL_CALLS = Counter("smartops_mcp_tool_calls_total", "Total MCP tool calls executed")
INCIDENTS_TOTAL = Counter("smartops_incidents_total", "Total incidents detected and managed")
REMEDIATION_SUCCESS = Counter("smartops_remediation_success_total", "Total successful remediations")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SmartOps AI Backend Gateway & Collector Engine...")
    collector.start()
    yield
    logger.info("Stopping SmartOps AI Backend...")
    collector.stop()

app = FastAPI(
    title="SmartOps AI Incident Response Platform",
    description="MCP-Powered Agentic Incident Response Platform for Microservices",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation ID Middleware
app.add_middleware(CorrelationIdMiddleware)

# Mount API Routers
app.include_router(auth_router)
app.include_router(services_router)
app.include_router(incidents_router)
app.include_router(remediation_router)
app.include_router(audit_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "platform": "SmartOps AI",
        "description": "MCP-Powered Agentic Incident Response Platform",
        "version": "1.0.0",
        "mode_a": "Deterministic AIOps Active",
        "mode_b": "Agentic AI + MCP Active",
        "mock_modes": {
            "mock_kubernetes": settings.MOCK_KUBERNETES,
            "mock_llm": settings.MOCK_LLM,
            "mock_logs": settings.MOCK_LOGS,
            "mock_database": settings.MOCK_DATABASE
        }
    }

@app.get("/health")
def health():
    return {
        "status": "UP",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
