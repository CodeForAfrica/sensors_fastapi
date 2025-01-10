import os
from typing import Annotated, Optional
import dotenv
import datetime
from asyncpg import Pool, create_pool as asyncpg_create_pool
from fastapi import FastAPI, Depends, HTTPException, Query, Request
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
    JSON,
)
from pydantic import BaseModel
from auth.router import auth_router


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


sensor_data_hypertables = {
    "PM_data": "sensor_PM_data",
    "temp_humidity": "sensor_temp_humidity_data",
}

dotenv.load_dotenv(override=True)
TIMESCALE_DB_CONNECTION = os.getenv("TIMESCALE_DB_CONNECTION")
print(TIMESCALE_DB_CONNECTION)

sqlite_file_name = "sensorsafrica.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)
postgres_engine = create_engine(TIMESCALE_DB_CONNECTION, echo=True)


tsb_conn_pool: Optional[Pool] = None

# Sensor Data Table
create_hypertable_query = f"""

DROP TABLE IF EXISTS {sensor_data_hypertables["PM_data"]};
DROP TABLE IF EXISTS {sensor_data_hypertables["temp_humidity"]};

CREATE TABLE IF NOT EXISTS {sensor_data_hypertables["PM_data"]} (
    time TIMESTAMPTZ NOT NULL,
    node_id VARCHAR(30) NOT NULL,
    PM1 FLOAT,
    PM2_5 FLOAT,
    PM10 FLOAT,
    location VARCHAR(64) NOT NULL,
    sensor_name VARCHAR(64) NOT NULL,
    FOREIGN KEY (node_id) REFERENCES node(node_id)
);
CREATE TABLE IF NOT EXISTS {sensor_data_hypertables["temp_humidity"]} (
    time TIMESTAMPTZ NOT NULL,
    node_id VARCHAR(30) NOT NULL,
    temperature FLOAT,
    rel_hum FLOAT,
    abs_hum FLOAT,
    heat_index FLOAT,
    location VARCHAR(64) NOT NULL,
    sensor_name VARCHAR(64) NOT NULL,
    FOREIGN KEY (node_id) REFERENCES node(node_id)
);

SELECT create_hypertable('{sensor_data_hypertables["PM_data"]}', 'time', if_not_exists => TRUE);
SELECT create_hypertable('{sensor_data_hypertables["temp_humidity"]}', 'time', if_not_exists => TRUE);
"""


async def init_connection_pool():
    global tsb_conn_pool
    try:
        print("Initializing PostgreSQL connection pool...")
        tsb_conn_pool = await asyncpg_create_pool(
            dsn=TIMESCALE_DB_CONNECTION, min_size=1, max_size=10
        )
        print("PostgreSQL connection pool created successfully.")

    except Exception as e:
        print(f"Error initializing PostgreSQL connection pool: {e}")
        raise


async def run_query(query):
    global tsb_conn_pool
    try:
        conn = await tsb_conn_pool.execute(query)
        return conn
    except Exception as e:
        print(f"Error occured when running query : {e}")
        print(query)
        raise


async def init_postgres() -> None:
    """
    Initialize the PostgreSQL connection pool and create the hypertables.
    """
    await init_connection_pool()

    # creat tables
    create_db_and_tables()

    # create hypertables
    await run_query(create_hypertable_query)

    # # insert dummy data
    # await run_query(dummy_sensor_data_query)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    SQLModel.metadata.create_all(postgres_engine)


def get_session():
    with Session(postgres_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_postgres()


app.include_router(auth_router)


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
            print()
            print("Fetched Location")
            print(registered_location)
            print()

            if not registered_location:
                locale = Location(country=country, city=city, location=location)
                locale = create_sensor_location(locale)
                registered_location = locale
                print()
                print("Auto registered")
                print(locale)
                print()

            # 2. Check if location_tag exists or create it
            if location_tag is not "":
                registered_loc_tag = get_location_tag(location_tag)
                if not registered_loc_tag:
                    locale_tag = LocationTag(
                        location_id=registered_location.id, location_tag=location_tag
                    )
                    locale_tag = create_location_tag(locale_tag)

        else:
            raise HTTPException(
                status=400, detail="Location and geolocation coordinates are required"
            )

        # 3. Check if custodian exists or create one
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

    # # ? so what if node is already in the database but location or custodian is not

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


app.add_api_route("/locations", endpoint=lambda: get_all_locations())


@app.post("/push-sensor-data")
async def post_data(data: dict):
    # headers = request.headers
    # print()
    # print("Received headers")
    # for header in headers:
    #     print(f"{header} : {headers[header]}")
    print()
    print("Received post data")
    print(data)

    # ? check if sensordata key is part of the object

    measurements = data["sensordata"].keys()
    for measurement in measurements:
        match (measurement):
            case "PM_data":
                pm_values = data["sensordata"][measurement]["values"]
                pm_data = PMDATA(
                    **pm_values
                )  # validate #? create custom validator to show keys mismatch with model
                min_data = delete_none_values(pm_values)
                min_data["time"] = data["timestamp"]
                min_data["node_id"] = data["node_id"]
                min_data["location"] = data["location"]
                min_data["sensor_name"] = data["sensordata"][measurement]["sensor_name"]
                query_stmt = generate_insert_query(
                    min_data, sensor_data_hypertables["PM_data"]
                )
                await insert_data(query_stmt)
            case "temp_humidity":
                temp_values = data["sensordata"][measurement]["values"]
                temp_data = Temp_Humidity(
                    **temp_values
                )  # validate #? create custom validator to show keys mismatch with model
                min_data = delete_none_values(temp_values)
                min_data["time"] = data["timestamp"]
                min_data["node_id"] = data["node_id"]
                min_data["location"] = data["location"]
                min_data["sensor_name"] = data["sensordata"][measurement]["sensor_name"]
                query_stmt = generate_insert_query(
                    min_data, sensor_data_hypertables["temp_humidity"]
                )
                await insert_data(query_stmt)
            case _:
                print("Could not find predifined measurement")

    # await insert_data(data)
    # print("body")
    # body = await request.json()
    # print(body)

    # await insert_data(body)

    return {"received_data": "OK"}


async def node_metadata(node: Node):
    stmt = select(Node, Location, Custodian).where(
        node.custodian_id == Custodian.id and node.location_id == Location.id
    )

    # session = Session(engine)
    session = next(get_session())
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
    # session = Session(engine)
    session = next(get_session())
    Nodes = session.exec(select(Node).offset(offset).limit(limit)).all()
    return Nodes


async def get_node(node_id) -> Node:
    print(node_id)
    # session = Session(engine)
    session = next(get_session())
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
    # session = Session(engine)
    session = next(get_session())
    stmt = select(Location).where(
        Location.country == country and Location.location == location
    )
    result = session.exec(stmt).all()
    session.close()
    if not result:
        return None
    return result[0]


def get_location_tag(tag) -> LocationTag:
    # session = Session(engine)
    session = next(get_session())
    stmt = select(LocationTag).where(LocationTag.location_tag == tag)
    result = session.exec(stmt).all()
    session.close()
    if not result:
        return None
    return result[0]


def get_custodian(name, email, phone) -> Custodian:
    # session = Session(engine)
    session = next(get_session())
    stmt = select(Custodian).where(
        Custodian.name == name and Custodian.email == email or Custodian.phone == phone
    )
    result = session.exec(stmt).all()
    session.close()
    if not result:
        return None
    return result[0]


def get_all_locations(
    offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
) -> list[Location]:
    # session = Session(engine)
    session = next(get_session())
    Locations = session.exec(select(Location).offset(offset).limit(limit)).all()
    return Locations


# setters like


def register_node(node: Node) -> Node:
    session = next(get_session())
    # session = Session(engine)
    session.add(node)
    session.commit()
    session.refresh(node)
    return node


def create_sensor_location(location: Location) -> Location:
    # session = Session(engine)
    session = next(get_session())
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


def create_location_tag(tag: LocationTag) -> LocationTag:
    # session = Session(engine)
    session = next(get_session())
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


def register_custodian(custodian: Custodian) -> Custodian:
    # session = Session(engine)
    session = next(get_session())
    session.add(custodian)
    session.commit()
    session.refresh(custodian)
    return custodian


def delete_none_values(dic):
    data = dict(dic)
    keys_to_delete = []
    # cannot delete dictionary while running a loop (RuntimeError: dictionary changed size during iteration)
    for key, val in data.items():
        if val is None:
            keys_to_delete.append(key)
    # delete items where value is None
    for key in keys_to_delete:
        del data[key]

    return data


def generate_insert_query(data: dict, table: str):
    keys = data.keys()
    vals = data.values()

    columns = ""
    for key in keys:
        columns += key + ","
    values = ""
    for val in vals:
        if (type(val).__name__) != "str":
            val = str(val)
            values += val + ","
        else:
            values += "'" + val + "',"

    # Remove last comma which will result in an invalid SQL statement
    columns = columns[:-1]
    values = values[:-1]

    insert_query = f"""INSERT INTO {table}({columns}) 
    VALUES({values});
        """
    return insert_query


async def insert_data(stmt):
    res = await run_query(stmt)
    print("Insert data response")
    print(res)
    return
