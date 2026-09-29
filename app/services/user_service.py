from sqlalchemy.orm import Session
from app.repositories import user_repository
from app.core.security import hash_password


class EmailAlreadyExistsError(Exception):
    pass


def register_user(db: Session, name: str, email: str, password: str):
    existing_user = user_repository.get_user_by_email(db, email)
    if existing_user:
        raise EmailAlreadyExistsError(f"Email {email} is already registered")

    hashed = hash_password(password)
    new_user = user_repository.create_user(db, name, email, hashed)
    return new_user

