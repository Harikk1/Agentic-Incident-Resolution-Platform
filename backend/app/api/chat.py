from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from agent.agent import smartops_agent
from backend.app.core.security import get_current_user, UserTokenData

router = APIRouter(prefix="/api/chat", tags=["AI Agent Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "ses-default-01"
    approved: bool = False
    action_override: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tool_traces: list[Dict[str, Any]]
    approval_card: Optional[Dict[str, Any]] = None
    verification_result: Optional[Dict[str, Any]] = None
    current_step: str

@router.post("", response_model=ChatResponse)
def chat_with_agent(payload: ChatRequest, current_user: UserTokenData = Depends(get_current_user)):
    state = smartops_agent.process_message(
        user_message=payload.message,
        session_id=payload.session_id or "ses-default-01",
        approved=payload.approved,
        action_override=payload.action_override
    )

    return ChatResponse(
        response=state.final_response,
        session_id=payload.session_id or "ses-default-01",
        tool_traces=[t.model_dump() for t in state.tool_traces],
        approval_card=state.approval_card,
        verification_result=state.verification_result,
        current_step=state.current_step
    )
