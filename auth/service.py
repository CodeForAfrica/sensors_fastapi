from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import User
from .utils import hash_password


class AuthService:
    async def get_user_by_username(username: str, session: AsyncSession):
        stmt = select(User).where(User.username == username)
        user = await session.exec(stmt).first()
        session.close()

        return user

    async def get_user_by_email(email: str, session: AsyncSession):
        stmt = select(User).where(User.email == email)
        user = await session.exec(stmt).first()
        session.close()

        return user

    async def create_user(self, user_data, session: AsyncSession):
        data = dict(user_data)

        new_user = User(**data)
        new_user["hashed_password"] = hash_password(data["password"])

        await session.add(new_user).commit()

        return new_user
