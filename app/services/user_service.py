from sqlalchemy.orm import Session
from app.repositories import user_repository

from app.core.security import hash_password, verify_password, create_access_token

class EmailAlreadyExistsError(Exception):
    pass


def register_user(db: Session, name: str, email: str, password: str):
    existing_user = user_repository.get_user_by_email(db, email)
    if existing_user:
        raise EmailAlreadyExistsError(f"Email {email} is already registered")

    hashed = hash_password(password)
    new_user = user_repository.create_user(db, name, email, hashed)
    return new_user

class InvalidCredentialsError(Exception):
    pass


def login_user(db: Session, email: str, password: str):
    user = user_repository.get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Invalid email or password")

    token = create_access_token(user.id)
    return token
