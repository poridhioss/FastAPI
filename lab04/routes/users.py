from fastapi import APIRouter, Depends
from schemas import User as UserSchema
from middleware.auth import get_current_active_user
from models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserSchema)
def get_profile(current_user: User = Depends(get_current_active_user)):
    """Get the current user's profile. This route is protected and requires JWT authentication."""
    return current_user


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Alternative endpoint to get current user information."""
    return current_user