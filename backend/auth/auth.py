import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from models.database import User, UserCreate
from database.database import get_user_db
from config import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=settings.JWT_LIFETIME_SECONDS)


# Authentication setup
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)


# Supabase-based auth dependency for frontend-managed auth
from typing import Optional as _Optional
from fastapi import Header as _Header, HTTPException as _HTTPException
from config import get_supabase_client as _get_supabase_client

class CurrentUser:
    def __init__(self, id: str, email: _Optional[str] = None):
        self.id = id
        self.email = email

def get_current_user(authorization: _Optional[str] = _Header(None)) -> CurrentUser:
    """
    Validate Supabase access token (JWT) provided via Authorization: Bearer <token>.
    Returns CurrentUser with `id` for RLS-scoped queries.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1].strip()

    sb_admin = _get_supabase_client(service_role=True)
    user_resp = sb_admin.auth.get_user(token)
    if not user_resp or not getattr(user_resp, "user", None):
        raise _HTTPException(status_code=401, detail="Invalid or expired token")

    user = user_resp.user
    return CurrentUser(id=user.id, email=getattr(user, "email", None))
