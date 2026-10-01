from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services import user_service
from app.schemas.user import UserRegisterRequest, UserResponse, UserLoginRequest, TokenResponse
from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=201)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        new_user = user_service.register_user(
            db, request.name, request.email, request.password
        )
        return new_user
    except user_service.EmailAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/auth/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    try:
        token = user_service.login_user(db, request.email, request.password)
        return TokenResponse(access_token=token)
    except user_service.InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/users/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully. Please discard your access token."}
