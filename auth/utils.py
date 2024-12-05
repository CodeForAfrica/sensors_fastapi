from passlib.context import CryptContext

password_context = CryptContext(schemes=["bycrypt"], deprecated="auto")


def hash_password(plain_passqord: str) -> str:
    hash = password_context.hash(plain_passqord)
    return hash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)
