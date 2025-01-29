# About

This is an experimental project using FastAPI and TimescaleDB as backend application for IoT sensors monitoring applications. 
The main purpose of this project is:
- to allow for automatic onboarding of new sensor devices/nodes to the sensors network database.
- handle a large number of API requests asynchronously.
- leverage Postgres for both realational and timeseries data use-cases.

# Setup

## Local setup

### Prerequisites
- Python 3.10 and above. Version 3.13.0 was used for this project.
- Have TimescaleDB installed by follwing this [guide](https://docs.timescale.com/self-hosted/latest/install/). A Docker instance is preferrable.

### steps

1. Create a virtual environment `python -m venv .venv` and activate `source .venv/bin/activate`
2. Install dependencies `pip install -r requirements.txt`
3. Create a `.env` file and set the environment variables as per the `.env.template`
4. Run the app `fastapi dev main.py`
5. Run the simulation script in another terminal `python sensors_simulate.py`


## Docker 

1. Run `docker compose up -d` to build and run the services. Override the default environment variables with the `-e` flag.
2. Run the the simulation script by entering the `api` service container's shell.
  - `docker exec -it <container id> /bin/bash`
  - `python sensors_simulate.py`

