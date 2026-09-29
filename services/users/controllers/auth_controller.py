from sqlalchemy.orm import Session
from models.user import UserRegisterRequest, UserLoginRequest


def register_user(user_data: UserRegisterRequest, db: Session):
    """
    Register a new user in the database.
    TODO: Implement hashing password, creating user in DB, and returning user response.
    """
    pass


def login_user(login_data: UserLoginRequest, db: Session):
    """
    Authenticate user and return a JWT access token.
    TODO: Implement verifying password, generating JWT token, and returning TokenResponse.
    """
    pass
