from typing import Annotated, Optional
import os, dotenv
from sqlmodel import SQLModel, Session, create_engine
from asyncpg import Pool, create_pool as asyncpg_create_pool
from fastapi import Depends

dotenv.load_dotenv(override=True)
TIMESCALE_DB_CONNECTION = os.getenv("TIMESCALE_DB_CONNECTION")

postgres_engine = create_engine(TIMESCALE_DB_CONNECTION, echo=True)

tsb_conn_pool: Optional[Pool] = None

sensor_data_hypertables = {
    "PM_data": "sensor_PM_data",
    "temp_humidity": "sensor_temp_humidity_data",
}

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


def get_session():
    with Session(postgres_engine) as session:
        yield session


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


def create_db_and_tables():
    # SQLModel.metadata.create_all(engine)
    SQLModel.metadata.create_all(postgres_engine)


SessionDep = Annotated[Session, Depends(get_session)]
