from typing import Optional
import datetime

# from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import SQLModel, Column, DateTime, func, Field, JSON


# Project metadata models
class Node(SQLModel, table=True):
    id: int | None = Field(
        default=None, primary_key=True
    )  # https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#primary-key-id

    node_id: str = Field(index=True, unique=True)
    # application_mode: int | None = Field(default=None, index=True)
    # date_registered: datetime = Field(default_factory=lambda: datetime.now())
    date_registered: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc),
    )
    date_updated: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(), onupdate=func.now(datetime.timezone.utc))
    )
    custodian_id: int | None = Field(default=None, foreign_key="custodian.id")
    commissioned: bool = Field(default=True)
    latitude: float
    longitude: float
    location_id: int | None = Field(default=None, foreign_key="sensor_locations.id")
    description: str | None


class Location(SQLModel, table=True):
    __tablename__ = "sensor_locations"
    id: int = Field(default=None, primary_key=True)
    location: str
    country: str
    city: str | None


class LocationTag(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="sensor_locations.id")
    location_tag: str = Field(default=None)
    description: str | None = Field(default=None)


class Custodian(SQLModel, table=True):  # ? This can be a user group
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str | None
    phone: str | None
    project: int | None = Field(default=None, foreign_key="project.id")
    affiliation: int | None = Field(default=None, foreign_key="organization.id")


class Organization(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    headquaters: str | None
    email: str | None


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_name: str
    description: str | None


# Sensor Data Model(s)
# class SensorData(SQLModel):
#     # timestamp: datetime
#     node_id: str
#     PM1: float | None
#     PM2_5: float | None
#     PM10: float | None
#     temperature: float | None
#     humidity: float | None


class SensorData(SQLModel):
    timestamp: datetime.datetime | None = Field(
        default=datetime.datetime.now(datetime.timezone.utc),
    )
    node_id: str
    parameter: str
    value: None
    sensor_type: str
    location: str


class PMDATA(BaseModel):
    PM1: float | None = None
    PM2_5: float | None = None
    PM10: float | None = None


class Temp_Humidity(BaseModel):
    temperature: float | None = None
    rel_hum: float | None = None
    abs_hum: float | None = None
    heat_index: float | None = None


class ParticulateMatterData(SensorData):
    value: dict = Field(sa_column=Column(JSON), default={})
