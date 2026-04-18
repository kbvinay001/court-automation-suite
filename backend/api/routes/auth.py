"""
Authentication Routes - Register, Login, Profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from api.models.user import UserCreate, UserLogin, UserUpdate
from api.services.auth_service import AuthService, get_current_user

router = APIRouter()
auth_service = AuthService()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user account."""
    result = await auth_service.register(user_data)
    return {"success": True, "data": result, "message": "Account created successfully"}


@router.post("/login")
async def login(login_data: UserLogin):
    """Authenticate user and return JWT token."""
    result = await auth_service.authenticate(login_data)
    return {"success": True, "data": result, "message": "Login successful"}


@router.get("/me")
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile."""
    profile = await auth_service.get_user_profile(current_user["email"])
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": profile}


@router.put("/profile")
async def update_profile(
    updates: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update current user profile."""
    update_dict = updates.model_dump(exclude_none=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Convert notification preferences to dict if present
    if "notification_preferences" in update_dict and update_dict["notification_preferences"]:
        update_dict["notification_preferences"] = update_dict["notification_preferences"].model_dump()  # type: ignore[union-attr]

    profile = await auth_service.update_profile(current_user["email"], update_dict)
    return {"success": True, "data": profile, "message": "Profile updated"}


@router.post("/change-password")
async def change_password(
    payload: Dict[str, str],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Change current user's password."""
    from api.services.auth_service import verify_password, hash_password
    from utils.database import find_one, update_one

    old_password = payload.get("old_password", "")
    new_password = payload.get("new_password", "")

    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    user = await find_one("users", {"email": current_user["email"]})
    if not user or not verify_password(old_password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    await update_one(
        "users",
        {"email": current_user["email"]},
        {"$set": {"password_hash": hash_password(new_password)}},
    )
    return {"success": True, "message": "Password changed successfully"}
