"""
Authentication Service - JWT token management, password hashing, user CRUD.
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt as _bcrypt_lib  # type: ignore[import]
from jose import JWTError, jwt  # type: ignore[import]
from fastapi import Depends, HTTPException, status  # type: ignore[import]
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # type: ignore[import]

from api.models.user import User, UserCreate, UserLogin, TokenResponse  # type: ignore[import]

logger = logging.getLogger(__name__)

# ─── Configuration ───
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "court-automation-secret-change-in-production-2026")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

# ─── Password Hashing (direct bcrypt, bypasses passlib compatibility issue) ───

# ─── Bearer Token Scheme ───
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt directly."""
    return _bcrypt_lib.hashpw(password.encode('utf-8'), _bcrypt_lib.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return _bcrypt_lib.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


class AuthService:
    """Handles user registration, authentication, and token management."""

    # ── In-memory fallback store (used when MongoDB is unavailable) ──────────
    _demo_users: dict = {}   # email -> user_doc

    def _db_available(self) -> bool:
        from utils.database import get_db  # type: ignore[import]
        return get_db() is not None

    async def register(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user."""
        if self._db_available():
            return await self._register_db(user_data)
        return self._register_memory(user_data)

    async def _register_db(self, user_data: UserCreate) -> Dict[str, Any]:
        from utils.database import find_one, insert_one  # type: ignore[import]
        existing = await find_one("users", {"email": user_data.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )
        user_doc = self._build_user_doc(user_data)
        await insert_one("users", user_doc)
        logger.info(f"User registered (DB): {user_data.email}")
        return self._token_response(user_data.email, user_data.full_name, user_data.role.value)

    def _register_memory(self, user_data: UserCreate) -> Dict[str, Any]:
        if user_data.email in AuthService._demo_users:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )
        user_doc = self._build_user_doc(user_data)
        AuthService._demo_users[user_data.email] = user_doc
        logger.info(f"User registered (in-memory demo mode): {user_data.email}")
        return self._token_response(user_data.email, user_data.full_name, user_data.role.value)

    def _build_user_doc(self, user_data: UserCreate) -> dict:
        return {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "password_hash": hash_password(user_data.password),
            "phone": user_data.phone,
            "role": user_data.role.value,
            "bar_council_id": user_data.bar_council_id,
            "court_preferences": [],
            "tracked_cases": [],
            "notification_preferences": {
                "email_enabled": True,
                "whatsapp_enabled": False,
                "sms_enabled": False,
                "daily_digest": True,
                "hearing_reminder_hours": 24,
                "causelist_alert": True,
            },
            "is_active": True,
            "is_verified": False,
            "last_login": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _token_response(self, email: str, full_name: str, role: str) -> Dict[str, Any]:
        token = create_access_token({"sub": email, "role": role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {"email": email, "full_name": full_name, "role": role},
        }

    async def authenticate(self, login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate a user and return a JWT token."""
        if self._db_available():
            return await self._authenticate_db(login_data)
        return self._authenticate_memory(login_data)

    async def _authenticate_db(self, login_data: UserLogin) -> Dict[str, Any]:
        from utils.database import find_one, update_one  # type: ignore[import]
        user = await find_one("users", {"email": login_data.email})
        if not user or not verify_password(login_data.password, user.get("password_hash", "")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
        await update_one("users", {"email": login_data.email}, {"last_login": datetime.now(timezone.utc).isoformat()})
        token = create_access_token({"sub": user["email"], "role": user.get("role", "advocate")})
        logger.info(f"User logged in (DB): {login_data.email}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {"email": user["email"], "full_name": user.get("full_name", ""), "role": user.get("role", "advocate")},
        }

    def _authenticate_memory(self, login_data: UserLogin) -> Dict[str, Any]:
        user = AuthService._demo_users.get(login_data.email)
        if not user or not verify_password(login_data.password, user.get("password_hash", "")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
        token = create_access_token({"sub": user["email"], "role": user.get("role", "advocate")})
        logger.info(f"User logged in (in-memory demo mode): {login_data.email}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {"email": user["email"], "full_name": user.get("full_name", ""), "role": user.get("role", "advocate")},
        }

    async def get_user_profile(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user profile by email."""
        if self._db_available():
            from utils.database import find_one  # type: ignore[import]
            user = await find_one("users", {"email": email})
        else:
            user = AuthService._demo_users.get(email)
        if user:
            user = dict(user)
            user.pop("password_hash", None)
            user.pop("_id", None)
        return user

    async def update_profile(self, email: str, updates: dict) -> Optional[Dict[str, Any]]:
        """Update user profile."""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        if self._db_available():
            from utils.database import update_one  # type: ignore[import]
            await update_one("users", {"email": email}, {"$set": updates})
        elif email in AuthService._demo_users:
            AuthService._demo_users[email].update(updates)
        return await self.get_user_profile(email)


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency: extract and validate the current user from JWT bearer token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return {"email": email, "role": payload.get("role", "advocate")}


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """FastAPI dependency: optionally extract user (returns None if no token)."""
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    email = payload.get("sub")
    return {"email": email, "role": payload.get("role", "advocate")} if email else None
