# 1. Create list dummy sensor nodes
# 2. Create list of locations
# 2. Create list of custodians
# 2. Create list of organizations
# 3. Create list of sensor types


sensor_locations = {
    "Ruiru": {
        "city": "Kiambu",
        "country": "Kenya",
        "coords": {"lat": -1.158124, "long": 36.977224},
    },
    "Mathare": {
        "city": "Nairobi",
        "country": "Kenya",
        "coords": {"lat": -1.261843, "long": 36.853302},
    },
    "Langas": {
        "city": "Nakuru",
        "country": "Kenya",
        "coords": {"lat": 0.304553, "long": 36.062612},
    },
    "Makongeni": {
        "city": "Thika",
        "country": "Kenya",
        "coords": {"lat": 1.296904, "long": 36.849754},
    },
}

projects = ["Clean Air Catalyst", "Respira", "Clean Air One"]

partner_orgs = {
    "Air Gradient": {
        "headquaters": "Somewhere in Malaysia",
        "email": "air@gradient.com",
    },
    "GIZ": {"headquaters": "Somewhere in Nairobi", "email": "giz@gmbh.de"},
    "UNEP": {"headquaters": "Gigiri, Nairobi", "email": "info@unep.org"},
    "WRI": {"headquaters": "westlands, nairobi", "email": "hello@wri.org"},
}

sensor_custodians = {
    "Alice": {
        "phone": "+1 (123) 456-7890",
        "email": "alice@example.com",
        "affiliated_org": partner_orgs["Air Gradient"],
    },
    "Bob": {
        "phone": "+1 (987) 654-3210",
        "email": "bob@example.com",
        "affiliated_org": partner_orgs["GIZ"],
    },
    "Charlie": {
        "phone": "+1 (555) 555-5555",
        "email": "charlie@example.com",
        "affiliated_org": partner_orgs["UNEP"],
    },
    "John": {
        "phone": "+1 (666) 666-666",
        "email": "charlie@example.com",
        "affiliated_org": None,
    },
}


sensors_list = {
    "esp8266-12": {
        "location": sensor_locations["Ruiru"],
        "custodian": sensor_custodians["Alice"],
        "project": projects[0],
    },
    "esp8266-34": {
        "location": sensor_locations["Mathare"],
        "custodian": sensor_custodians["Bob"],
        "project": projects[1],
    },
    "esp8266-56": {
        "location": sensor_locations["Langas"],
        "custodian": sensor_custodians["Charlie"],
        "project": projects[2],
    },
    "esp8266-78": {
        "location": sensor_locations["Makongeni"],
        "custodian": sensor_custodians["John"],
        "project": None,
    },
}
