from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt, uuid, os

DEFAULT_TOKEN_EXPIRY = 60 * 60 * 24
JWT_KEY = os.getenv("JWT_SECRET_KEY")  # ? use pydantic config instead
JWT_ALGO = os.getenv("JWT_ALGORITHM")
print("JWT_KEY", JWT_KEY)
print("JWT_ALGORITHM", JWT_ALGO)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_passqord: str) -> str:
    hash = password_context.hash(plain_passqord)
    return hash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expiry: timedelta = None, refresh: bool = False):
    expiry = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=DEFAULT_TOKEN_EXPIRY)
    )
    payload = {"user": data}
    payload["expires"] = expiry
    payload["refresh"] = refresh
    payload["token_id"] = str(uuid.uuid4())

    token = jwt.encode(payload=payload, key=JWT_KEY, algorithm=JWT_ALGO)

    return token


def decode_token(token: str) -> str:
    try:
        token_data = jwt.decode(jwt=token, key=JWT_KEY, algorithms=JWT_ALGO)
        return token_data
    except jwt.PyJWTError as error:
        print(error)
        return None
