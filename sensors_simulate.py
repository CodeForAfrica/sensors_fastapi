# 1. Create list dummy sensor nodes
# 2. Create list of locations
# 2. Create list of custodians
# 2. Create list of organizations
# 3. Create list of sensor types

from random import randrange
import requests

API_ENDPOINT = "http://127.0.0.1:8000"
REGISTER_NODE = API_ENDPOINT + "/register-node"

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

sensors_list = [
    {
        "esp8266-12": {
            "location": sensor_locations["Ruiru"],
            "custodian": sensor_custodians["Alice"],
            "project": projects[0],
        }
    },
    {
        "esp8266-34": {
            "location": sensor_locations["Mathare"],
            "custodian": sensor_custodians["Bob"],
            "project": projects[1],
        }
    },
    {
        "esp8266-56": {
            "location": sensor_locations["Langas"],
            "custodian": sensor_custodians["Charlie"],
            "project": projects[2],
        }
    },
    {
        "esp8266-78": {
            "location": sensor_locations["Makongeni"],
            "custodian": sensor_custodians["John"],
            "project": None,
        }
    },
]


def register_random_node():

    sensor_list_length = len(sensors_list)
    random_index = randrange(sensor_list_length)
    sensor = sensors_list[random_index]
    sensor_keys = sensor.keys()
    # first_sensor_key = next(iter(sensors_keys))
    first_sensor_key = list(sensor_keys)[0]
    sensor_name = first_sensor_key

    data = {
        "node_id": sensor_name,
        "lat": sensor[first_sensor_key]["location"]["coords"]["lat"],
        "long": sensor[first_sensor_key]["location"]["coords"]["long"],
        "country": sensor[first_sensor_key]["location"]["country"],
        "location": sensor[first_sensor_key]["location"]["name"],
        "city": sensor[first_sensor_key]["location"]["city"],
        "location_tag": "",
        "custodian_name": sensor[first_sensor_key]["custodian"]["name"],
        "custodian_email": sensor[first_sensor_key]["custodian"]["email"],
        "custodian_phone": sensor[first_sensor_key]["custodian"]["phone"],
        "software_version": "",
        "project_name": sensor[first_sensor_key]["project"],
    }

    # print(data)

    response = requests.get(REGISTER_NODE, params=data)
    print(response)
    # call post function


# register_random_node()
