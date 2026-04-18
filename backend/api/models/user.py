"""
User data model - represents application users and their preferences.
"""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from enum import Enum


class UserRole(str, Enum):
    ADVOCATE = "advocate"
    LITIGANT = "litigant"
    CLERK = "clerk"
    ADMIN = "admin"


class NotificationPreference(BaseModel):
    """User notification preferences."""
    email_enabled: bool = True
    whatsapp_enabled: bool = False
    sms_enabled: bool = False
    daily_digest: bool = True
    hearing_reminder_hours: int = 24
    causelist_alert: bool = True


class TrackedCase(BaseModel):
    """Case tracked by a user."""
    case_number: str
    court_name: str
    alias: Optional[str] = None
    notes: Optional[str] = None
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class User(BaseModel):
    """Full user representation."""
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.ADVOCATE
    bar_council_id: Optional[str] = None
    court_preferences: List[str] = []
    tracked_cases: List[TrackedCase] = []
    notification_preferences: NotificationPreference = Field(
        default_factory=NotificationPreference
    )
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "advocate@example.com",
                "full_name": "Rajesh Kumar",
                "phone": "+919876543210",
                "role": "advocate",
                "bar_council_id": "DL/1234/2020",
            }
        }
    )


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    phone: Optional[str] = None
    role: UserRole = UserRole.ADVOCATE
    bar_council_id: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bar_council_id: Optional[str] = None
    court_preferences: Optional[List[str]] = None
    notification_preferences: Optional[NotificationPreference] = None


class UserResponse(BaseModel):
    """API response for user data (excludes password)."""
    success: bool = True
    data: Optional[User] = None
    message: str = ""


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
