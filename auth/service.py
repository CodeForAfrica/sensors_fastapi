from sqlmodel import select
from .models import User
from .utils import hash_password
from db import get_session


class AuthService:
    async def get_user_by_username(self, username: str):
        session = next(get_session())
        print("Getting user by username")
        stmt = select(User).where(User.username == username)
        print(stmt)
        user = session.exec(stmt).first()
        print(user)
        session.close()

        return user

    async def get_user_by_email(self, email: str):
        session = next(get_session())
        stmt = select(User).where(User.email == email)
        user = session.exec(stmt).first()
        session.close()
        return user

    async def verify_user_exists(self, func, arg) -> bool:
        print("Verifying user exists", func)
        # print(type(session))
        user = await func(arg)
        print(user)
        return True if user is not None else False

    async def create_user(self, user_data):
        data = dict(user_data)
        data["hashed_password"] = hash_password(data["password"])
        new_user = User(**data)
        print(new_user)
        session = next(get_session())
        session.add(new_user)
        session.commit()

        return new_user
