from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services import user_service
from app.schemas.user import UserRegisterRequest, UserResponse

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
