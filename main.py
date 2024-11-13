from typing import Annotated, Optional
import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlmodel import (
    Session,
    SQLModel,
    create_engine,
    Column,
    DateTime,
    func,
    Field,
    select,
)


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


sqlite_file_name = "sensorsafrica.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Required metadata
# node id, application type,


@app.get("/register-node/")
async def register_node(
    node_id: str = "",
    sensor_application: str = "stationary",
    lat: float = 0,
    long: float = 0,
    country: str = "",
    location: str = "",
    city: str = "",
    location_tag: str = "",
    custodian_name: str = "",
    custodian_email: str = "",
    custodian_phone: str = "",
    software_version: str = "",
    project_name="",
):
    #  Check if node is registered
    custodian_id = None
    registered_location = None
    registered_node = await get_node(node_id)
    print(registered_node)
    if registered_node is None:
        # register node

        # 1. Check if location exists or create it
        if location is not "":
            registered_location = get_location(country, location)
            if not registered_location:
                locale = Location(country=country, city=city, location=location)
                locale = create_sensor_location(locale)
                registered_location = locale
                print(locale)
            # 2. Check if location_tag exists or create it
            if location_tag is not "":
                registered_loc_tag = get_location_tag(location_tag)
                if not registered_loc_tag:
                    locale_tag = LocationTag(
                        location_id=registered_location.id, location_tag=location_tag
                    )
                    locale_tag = create_location_tag(locale_tag)

        # 3. Check if custodian exists or create one
        else:
            raise HTTPException(
                status=400, detail="Location and geolocation coordinates are required"
            )

        if custodian_name is not "" and (
            custodian_email is not "" or custodian_phone is not ""
        ):  # no point of registering a custodian if there is no contact details

            registered_custodian = get_custodian(
                custodian_name, custodian_email, custodian_phone
            )

            if registered_custodian is None:
                new_custodian = Custodian(
                    name=custodian_name, email=custodian_email, phone=custodian_phone
                )
                new_custodian = register_custodian(new_custodian)
                custodian_id = new_custodian.id

    # 4. Register node
    new_node = Node(
        node_id=node_id,
        custodian_id=custodian_id,
        latitude=lat,
        longitude=long,
        location_id=registered_location.id,
    )
    new_node = register_node(new_node)
    registered_node = new_node

    # ? so what if node is already in the database but location or cusdian is not
    print(registered_node)
    return {"registered": "OK", "node_details": registered_node}


@app.get("/node/{node_id}")
async def node_details(node_id: str):
    node = await get_node(node_id)
    # print(node)
    if node is None:
        return HTTPException(status_code=404, detail="Node not found")

    return await node_metadata(node)


@app.get("/nodes")
async def get_nodes():
    return get_nodes()


async def node_metadata(node: Node):
    stmt = select(Node, Location, Custodian).where(
        node.custodian_id == Custodian.id and node.location_id == Location.id
    )

    session = Session(engine)
    node_info = session.exec(stmt).all()
    session.close()
    node_info = [dict(row._mapping) for row in node_info]

    # all() returns a list of rows. #!! all() should of course return a list containing only one row otherwise there are duplicate entries in the database
    return node_info[0]


# getters like


def get_nodes(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Node]:
    session = Session(engine)
    Nodes = session.exec(select(Node).offset(offset).limit(limit)).all()
    return Nodes


async def get_node(node_id) -> Node:
    print(node_id)
    session = Session(engine)
    stmt = select(Node).where(Node.node_id == node_id)
    result = session.exec(stmt).all()
    session.close()
    if len(result) > 1:
        print("Result has more than one node")
        for node in result:
            print(node)
        # Probably alert admin about this
        return None

    elif not result:
        return None

    return result[0]


def get_location(country, location) -> Location:
    session = Session(engine)
    stmt = select(Location).where(
        Location.country == country and Location.location == location
    )
    result = session.exec(stmt).all()
    session.close()
    if not result:
        return None
    return result[0]


def get_location_tag(tag) -> LocationTag:
    session = Session(engine)
    stmt = select(LocationTag).where(LocationTag.location_tag == tag)
    result = session.exec(stmt).all()
    session.close()
    if not result:
        return None
    return result[0]


def get_custodian(name, email, phone) -> Custodian:
    session = Session(engine)
    stmt = select(Custodian).where(
        Custodian.name == name and Custodian.email == email or Custodian.phone == phone
    )
    result = session.exec(stmt).all()
    session.close()
    if not result:
        return None
    return result[0]


# setters like


def register_node(node: Node) -> Node:
    # session = next(get_session())
    session = Session(engine)
    session.add(node)
    session.commit()
    session.refresh(node)
    return node


def create_sensor_location(location: Location) -> Location:
    session = Session(engine)
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


def create_location_tag(tag: LocationTag) -> LocationTag:
    session = Session(engine)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


def register_custodian(custodian: Custodian) -> Custodian:
    session = Session(engine)
    session.add(custodian)
    session.commit()
    session.refresh(custodian)
    return custodian
