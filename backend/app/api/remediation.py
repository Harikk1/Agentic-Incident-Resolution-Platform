from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from backend.app.database.repositories import remediation_repo
from backend.app.core.security import get_current_user, UserTokenData

router = APIRouter(prefix="/api/remediation", tags=["Remediation"])

@router.get("/{action_id}", response_model=Dict[str, Any])
def get_remediation_action(action_id: str, current_user: UserTokenData = Depends(get_current_user)):
    action = remediation_repo.get_by_id(action_id)
    if not action:
        raise HTTPException(status_code=404, detail=f"Remediation action {action_id} not found")
    return action
