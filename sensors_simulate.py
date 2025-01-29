# 1. Create list dummy sensor nodes
# 2. Create list of locations
# 2. Create list of custodians
# 2. Create list of organizations
# 3. Create list of sensor types

from random import randrange, uniform
import requests, time
from datetime import datetime, timezone

API_ENDPOINT = "http://127.0.0.1:8000"
REGISTER_NODE = API_ENDPOINT + "/register-node"
POST_DATA = API_ENDPOINT + "/push-sensor-data"
current_node = None
current_node_name = None
start_time = time.time()
generate_data_duration = 30 * 60
register_random_node_interval = 5 * 60
send_data_interval = 30

last_register_node_time = 0
last_send_data_time = 0

sensor_locations = {
    "Ruiru": {
        "name": "Ruiru",
        "city": "Kiambu",
        "country": "Kenya",
        "coords": {"lat": -1.158124, "long": 36.977224},
    },
    "Mathare": {
        "name": "Mathare",
        "city": "Nairobi",
        "country": "Kenya",
        "coords": {"lat": -1.261843, "long": 36.853302},
    },
    "Langas": {
        "name": "Langas",
        "city": "Nakuru",
        "country": "Kenya",
        "coords": {"lat": 0.304553, "long": 36.062612},
    },
    "Makongeni": {
        "name": "Makongeni",
        "city": "Thika",
        "country": "Kenya",
        "coords": {"lat": 1.296904, "long": 36.849754},
    },
}

projects = ["Clean Air Catalyst", "Respira", "Clean Air One"]

partner_orgs = {
    "Air Gradient": {
        "name": "Air Gradient",
        "headquaters": "Somewhere in Malaysia",
        "email": "air@gradient.com",
    },
    "GIZ": {
        "name": "GIZ",
        "headquaters": "Somewhere in Nairobi",
        "email": "giz@gmbh.de",
    },
    "UNEP": {
        "name": "UNEP",
        "headquaters": "Gigiri, Nairobi",
        "email": "info@unep.org",
    },
    "WRI": {
        "name": "WRI",
        "headquaters": "westlands, nairobi",
        "email": "hello@wri.org",
    },
}

sensor_custodians = {
    "Alice": {
        "name": "Alice",
        "phone": "+1 (123) 456-7890",
        "email": "alice@example.com",
        "affiliated_org": partner_orgs["Air Gradient"],
    },
    "Bob": {
        "name": "Bob",
        "phone": "+1 (987) 654-3210",
        "email": "bob@example.com",
        "affiliated_org": partner_orgs["GIZ"],
    },
    "Charlie": {
        "name": "Charlie",
        "phone": "+1 (555) 555-5555",
        "email": "charlie@example.com",
        "affiliated_org": partner_orgs["UNEP"],
    },
    "John": {
        "name": "John",
        "phone": "+1 (666) 666-666",
        "email": "charlie@example.com",
        "affiliated_org": None,
    },
}


sensor_types = ["PM_Sensor", "temp_humidity", "Co2", "So2"]
sensors_brands = [
    "Plant Tower",
]

nodes_list = [
    {
        "esp8266-12": {
            "location": sensor_locations["Ruiru"],
            "custodian": sensor_custodians["Alice"],
            "project": projects[0],
            "sensors": [sensor_types[0], sensor_types[1]],
        }
    },
    {
        "esp8266-34": {
            "location": sensor_locations["Mathare"],
            "custodian": sensor_custodians["Bob"],
            "project": projects[1],
            "sensors": [sensor_types[0], sensor_types[2]],
        }
    },
    {
        "esp8266-56": {
            "location": sensor_locations["Langas"],
            "custodian": sensor_custodians["Charlie"],
            "project": projects[2],
            "sensors": [sensor_types[0], sensor_types[1]],
        }
    },
    {
        "esp8266-78": {
            "location": sensor_locations["Makongeni"],
            "custodian": sensor_custodians["John"],
            "project": None,
            "sensors": [sensor_types[2], sensor_types[3]],
        }
    },
]


def register_random_node():

    node_list_length = len(nodes_list)
    random_index = randrange(node_list_length)
    node = nodes_list[random_index]
    global current_node
    current_node = node
    node_keys = node.keys()
    # first_sensor_key = next(iter(sensors_keys))
    first_node_key = list(node_keys)[0]
    global current_node_name
    current_node_name = first_node_key

    data = {
        "node_id": current_node_name,
        "lat": node[first_node_key]["location"]["coords"]["lat"],
        "long": node[first_node_key]["location"]["coords"]["long"],
        "country": node[first_node_key]["location"]["country"],
        "location": node[first_node_key]["location"]["name"],
        "city": node[first_node_key]["location"]["city"],
        "location_tag": "",
        "custodian_name": node[first_node_key]["custodian"]["name"],
        "custodian_email": node[first_node_key]["custodian"]["email"],
        "custodian_phone": node[first_node_key]["custodian"]["phone"],
        "software_version": "",
        "project_name": node[first_node_key]["project"],
    }

    # # print(data)

    response = requests.get(REGISTER_NODE, params=data)
    print(response)

    # send random data for this node
    send_random_data()


# register_random_node()


def generate_dummy_data(lower_limit, upper_limit):
    return round(uniform(lower_limit, upper_limit), 2)


def send_random_data():
    # Which sensor was randomly selected
    # Get the sensor types
    """sensor_data_payload_template = {
        "timestamp": "UTC time",
        "location": "Mathare",
        "nodeid": "esp32-8232",
        "sensordata": {
            "PM_data": {
                "values": {"PM1": 39.4, "PM2_5": 12.3, "PM10": 23.4},
                "sensor_name": "PM55003",
                "units": "ug/m3",
            },
        },
        "temp_humidity": {
            "values": {"temp": 25, "rel_hum": 60, "abs_hum": 45},
            "sensor_name": "DHT22",
            "units": "C",
        },
        "geo_data": {"long": 36.30503, "lat": -1.1244, "alt": 1466},
    }"""
    sensordata = {
        "PM_data": {
            "values": {
                "PM1": None,
                "PM2_5": None,
                "PM10": None,
            },
            "sensor_name": "PMS5003",
        },
        "temp_humidity": {
            "values": {"temperature": None, "rel_hum": None, "abs_hum": None},
            "sensor_name": "DHT22",
        },
    }
    # for each sensor type generate random values
    for sensor in current_node[current_node_name]["sensors"]:
        print(sensor)
        match (sensor):  # Supported from Python 3.10
            case "PM_Sensor":
                sensordata["PM_data"]["values"]["PM1"] = generate_dummy_data(0, 200)
                sensordata["PM_data"]["values"]["PM2_5"] = generate_dummy_data(0, 200)
            case "temp_humidity":

                sensordata["temp_humidity"]["values"]["temperature"] = (
                    generate_dummy_data(0, 100)
                )
                sensordata["temp_humidity"]["values"]["rel_hum"] = generate_dummy_data(
                    0, 100
                )
            case _:
                print(f"{sensor} Sensor not evaluated in this case")

    is_all_data_empty = all(
        value == None for value in sensordata["PM_data"]["values"].values()
    )  # now just checks only PM data

    if is_all_data_empty:
        print("Data contains empty values in all cases")
        print("No need to send..")
        return

    print(sensordata)

    # post to timescale DB
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node_id": current_node_name,
        "location": current_node[current_node_name]["location"]["name"],
        "sensordata": sensordata,
    }

    print(payload)

    response = requests.post(POST_DATA, json=payload)
    print("Insert sensor data response")
    print(response.status_code)


# iniatialize registration and data send for first time
register_random_node()
last_register_node_time = time.time()
send_random_data()
last_send_data_time = time.time()

while time.time() - start_time < generate_data_duration:
    if time.time() - last_register_node_time > register_random_node_interval:
        register_random_node
        last_register_node_time = time.time()

    elif time.time() - last_send_data_time > send_data_interval:
        send_random_data


# register_random_node()
