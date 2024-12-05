from fastapi import APIRouter, HTTPException
from .schemas import UserCreateModel
from .service import AuthService


auth_router = APIRouter()
auth_service = AuthService()


@auth_router.post("/signup")
async def signup_user(user_data: UserCreateModel):
    username, email = user_data.username, user_data.email

    # check if an existing user shares a similar username or email

    username_exists = await auth_service.verify_user_exists(
        auth_service.get_user_by_username, username
    )
    email_exists = await auth_service.verify_user_exists(
        auth_service.get_user_by_username, email
    )
    if username_exists:
        return HTTPException(
            status=403,
            detail="A user with that username exists. Please try another one.",
        )
    elif email_exists:
        return HTTPException(status=403, detail="A user with that email exists.")

    else:
        auth_service.create_user(user_data)
        return "Registration successful"
