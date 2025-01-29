from fastapi import APIRouter, HTTPException, Query
from typing import Annotated
from .models import Node, Location, LocationTag, Custodian, PMDATA, Temp_Humidity
from .utils import insert_data, generate_insert_query, delete_none_values
from sqlmodel import select
from db import get_session, sensor_data_hypertables

sensors_router = APIRouter()


@sensors_router.get("/register-node/")
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


@sensors_router.get("/node/{node_id}")
async def node_details(node_id: str):
    node = await get_node(node_id)
    # print(node)
    if node is None:
        return HTTPException(status_code=404, detail="Node not found")

    return await node_metadata(node)


@sensors_router.get("/nodes")
async def get_nodes():
    return get_nodes()


sensors_router.add_api_route("/locations", endpoint=lambda: get_all_locations())


@sensors_router.post("/push-sensor-data")
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
