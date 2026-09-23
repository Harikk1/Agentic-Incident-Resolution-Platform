from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from backend.app.database.repositories import services_repo
from backend.app.monitoring.metric_buffer import metric_buffer
from backend.app.remediation.actions import remediation_actions
from backend.app.core.security import get_current_user, UserTokenData

router = APIRouter(prefix="/api/services", tags=["Services"])

@router.get("", response_model=List[Dict[str, Any]])
def list_services(current_user: UserTokenData = Depends(get_current_user)):
    services = services_repo.list_all()
    # Enrich with latest live metrics
    for svc in services:
        name = svc["name"]
        latest = metric_buffer.get_latest(name)
        if latest:
            svc["current_metrics"] = latest.model_dump()
            svc["status"] = "CRITICAL" if latest.pod_availability < 0.5 or latest.error_rate > 0.05 else "HEALTHY"
    return services

@router.get("/{service}/metrics")
def get_service_metrics(service: str, current_user: UserTokenData = Depends(get_current_user)):
    latest = metric_buffer.get_latest(service)
    history = [s.model_dump() for s in metric_buffer.get_history(service, count=30)]
    return {
        "service": service,
        "current": latest.model_dump() if latest else None,
        "history": history
    }

@router.get("/{service}/health")
def get_service_health(service: str, current_user: UserTokenData = Depends(get_current_user)):
    return remediation_actions.verify_service_health(service)

@router.get("/{service}/history")
def get_service_history(service: str, limit: int = 50, current_user: UserTokenData = Depends(get_current_user)):
    history = [s.model_dump() for s in metric_buffer.get_history(service, count=limit)]
    return {"service": service, "data_points": len(history), "history": history}
