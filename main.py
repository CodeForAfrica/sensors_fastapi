from fastapi import FastAPI
from auth.router import auth_router
from db import init_postgres
from sensors.router import sensors_router
from contextlib import asynccontextmanager

# sqlite_file_name = "sensorsafrica.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing app ...")
    await init_postgres()
    yield
    print("Shutting down app ...")


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(sensors_router)
