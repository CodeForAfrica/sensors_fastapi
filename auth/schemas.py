from pydantic import BaseModel, EmailStr, Field


class UserCreateModel(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6)
    phone: str | None = None


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str
