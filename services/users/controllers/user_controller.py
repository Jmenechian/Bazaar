from sqlalchemy.orm import Session
from models.user import UserUpdateRequest


def get_current_user_profile(user_id: int, db: Session):
    """
    Fetch the profile of the currently authenticated user.
    TODO: Query user by user_id and return user profile.
    """
    pass


def update_user_profile(user_id: int, update_data: UserUpdateRequest, db: Session):
    """
    Update profile fields for the current user.
    TODO: Update user record and return updated profile.
    """
    pass


def get_user_by_id(user_id: int, db: Session):
    """
    Fetch public profile for a user by id.
    TODO: Query user and return public profile.
    """
    pass
