from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt, uuid
from utils import create_access_token

DEFAULT_TOKEN_EXPIRY = 60 * 60 * 24

password_context = CryptContext(schemes=["bycrypt"], deprecated="auto")


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
    payload["token_id"] = str(uuid.uuid4())

    token = jwt.encode(payload=payload, key="myopenkey", algorithm="HS256")

    return token


def decode_token(token: str) -> str:
    try:
        token_data = jwt.decode(jwt=token, key="myopenkey", algorithms=["HS256"])
        return token_data
    except jwt.PyJWTError as error:
        print(error)
        return None
