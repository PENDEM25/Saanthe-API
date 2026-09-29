from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

