import time
import jwt
from typing import Optional, List, Dict
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from backend.app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)

class Role:
    VIEWER = "VIEWER"
    ENGINEER = "ENGINEER"
    ADMIN = "ADMIN"

ROLE_PERMISSIONS = {
    Role.VIEWER: [
        "read:services",
        "read:metrics",
        "read:incidents",
        "read:logs",
        "read:audit"
    ],
    Role.ENGINEER: [
        "read:services",
        "read:metrics",
        "read:incidents",
        "read:logs",
        "read:audit",
        "action:investigate",
        "action:diagnose",
        "action:chat",
        "remediation:approve:medium"
    ],
    Role.ADMIN: [
        "read:services",
        "read:metrics",
        "read:incidents",
        "read:logs",
        "read:audit",
        "action:investigate",
        "action:diagnose",
        "action:chat",
        "remediation:approve:medium",
        "remediation:approve:high",
        "remediation:execute:all",
        "config:manage"
    ]
}

class UserTokenData(BaseModel):
    user_id: str
    email: str
    role: str
    permissions: List[str]

# Demo credentials for easy testing
DEMO_USERS = {
    "admin@smartops.ai": {
        "user_id": "usr-admin-01",
        "email": "admin@smartops.ai",
        "password": "adminpassword",
        "role": Role.ADMIN
    },
    "engineer@smartops.ai": {
        "user_id": "usr-eng-01",
        "email": "engineer@smartops.ai",
        "password": "engineerpassword",
        "role": Role.ENGINEER
    },
    "viewer@smartops.ai": {
        "user_id": "usr-view-01",
        "email": "viewer@smartops.ai",
        "password": "viewerpassword",
        "role": Role.VIEWER
    }
}

def create_access_token(data: Dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = time.time() + (expires_delta or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> UserTokenData:
    if not credentials:
        # Default fallback to Admin in local development if no auth header passed
        if settings.DEBUG:
            return UserTokenData(
                user_id="usr-default-admin",
                email="admin@smartops.ai",
                role=Role.ADMIN,
                permissions=ROLE_PERMISSIONS[Role.ADMIN]
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required"
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    role = payload.get("role", Role.VIEWER)
    permissions = ROLE_PERMISSIONS.get(role, [])
    return UserTokenData(
        user_id=payload.get("user_id", "unknown"),
        email=payload.get("email", ""),
        role=role,
        permissions=permissions
    )

def require_permission(required_perm: str):
    def permission_checker(current_user: UserTokenData = Depends(get_current_user)):
        if required_perm not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires permission '{required_perm}'"
            )
        return current_user
    return permission_checker
