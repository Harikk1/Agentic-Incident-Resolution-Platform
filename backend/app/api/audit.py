from fastapi import APIRouter, Depends
from typing import List, Dict, Any, Optional
from backend.app.database.repositories import audit_repo
from backend.app.core.security import get_current_user, UserTokenData

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("", response_model=List[Dict[str, Any]])
def list_audit_logs(limit: int = 50, tool: Optional[str] = None, current_user: UserTokenData = Depends(get_current_user)):
    all_logs = audit_repo.list_all()
    # Sort descending by timestamp
    all_logs.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    if tool:
        all_logs = [log for log in all_logs if log.get("tool") == tool]
    return all_logs[:limit]
