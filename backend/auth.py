"""
Authentication utilities for FastAPI with Supabase.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from supabase_config import get_supabase, JWT_SECRET, JWT_ALGORITHM

# Security scheme for JWT tokens
security = HTTPBearer()

class AuthUser:
    """Represents an authenticated user."""
    
    def __init__(self, user_id: str, email: str, metadata: Dict[str, Any] = None):
        self.user_id = user_id
        self.email = email
        self.metadata = metadata or {}

def verify_token(token: str) -> Optional[AuthUser]:
    """Verify a JWT token and return user information."""
    try:
        # Decode the JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            return None
            
        return AuthUser(
            user_id=user_id,
            email=email,
            metadata=payload.get("user_metadata", {})
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthUser:
    """Dependency to get the current authenticated user."""
    token = credentials.credentials
    user = verify_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[AuthUser]:
    """Optional dependency to get the current user if authenticated."""
    if not credentials:
        return None
    
    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None
