from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.app.core.security import create_access_token, get_current_user, UserTokenData, DEMO_USERS, ROLE_PERMISSIONS

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    permissions: list[str]

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user = DEMO_USERS.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_data = {
        "sub": user["user_id"],
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"]
    }
    token = create_access_token(token_data)
    return LoginResponse(
        access_token=token,
        user_id=user["user_id"],
        email=user["email"],
        role=user["role"],
        permissions=ROLE_PERMISSIONS.get(user["role"], [])
    )

@router.get("/me", response_model=UserTokenData)
def get_me(current_user: UserTokenData = Depends(get_current_user)):
    return current_user
