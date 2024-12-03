from sqlmodel import SQLModel, Field, Column, DateTime, func
import uuid, datetime
import sqlalchemy.dialects.postgresql as pg
from pydantic import EmailStr


class User(SQLModel):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    username: str
    email: EmailStr
    firstname: str
    lastname: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc),
    )
    updated_at: datetime.datetime | None = Field(
        sa_column=Column(DateTime(), onupdate=func.now(datetime.timezone.utc))
    )
