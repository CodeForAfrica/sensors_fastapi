# About

This project is a FastAPI and TimescaleDB based backend application for IoT sensors monitoring applications. 
The main purpose of this project is:
- to allow for automatic onboarding of new sensor devices/nodes to the sensors network database.
- handle a large of API requests asynchronously.
- leverage Postgres for both realational and timeseries data use-cases.

# Setup

## Local setup

### Prerequisites
- Python 3.10 and above. Version 3.13.0 was used for this project.
- Have TimescaleDB installed by follwing this [guide](https://docs.timescale.com/self-hosted/latest/install/). A Docker instance is preferrable.

### steps

1. Create a virtual environment `python -m venv .venv` and activate `source .venv/bin/activate`
2. Install dependencies `pip install -r requirements.txt`
3. Run the app `fastapi dev main.py`
4. Run the simulation script in another ternminal `python sensors_simulate.py`
