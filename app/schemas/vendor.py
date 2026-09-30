from pydantic import BaseModel


class VendorProfileRequest(BaseModel):
    business_name: str | None = None


class VendorProfileResponse(BaseModel):
    id: int
    user_id: int
    business_name: str | None

    class Config:
        from_attributes = True

