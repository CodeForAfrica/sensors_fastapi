from fastapi import APIRouter, HTTPException, Depends
from .schemas import UserCreateModel, UserLoginModel
from .service import AuthService
from .utils import verify_password, create_access_token
from .dependencies import RefreshTokenBearer
from datetime import datetime

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
    email_exists = False
    if username_exists:
        return HTTPException(
            status_code=403,
            detail="A user with that username exists. Please try another one.",
        )
    elif email_exists:
        return HTTPException(status_code=403, detail="A user with that email exists.")

    else:
        await auth_service.create_user(user_data)
        return "Registration successful"


@auth_router.post("/login")
async def login_user(form_data: UserLoginModel):
    email = form_data.email
    password = form_data.password
    user = await auth_service.get_user_by_email(email)

    if user is not None:
        uid = str(user.uid)  # ? Create a parser function to handle SQLModel objects
        is_pwd_valid = verify_password(password, user.hashed_password)

        if is_pwd_valid:
            access_token = create_access_token(data={"email": user.email, "uid": uid})
            refresh_token = create_access_token(
                data={"email": user.email, "uid": uid},
                expiry=60 * 60 * 24 * 7,
                refresh=True,
            )

        return {
            "message": "login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"email": user.email, "uid": user.uid},
        }

    raise HTTPException(status_code=403, detail="Invalid email or password")


@auth_router.get("/refresh_access_token")
async def refresh_access_token(token_data: dict = Depends(RefreshTokenBearer())):
    """Issue new access token using a referesh token"""

    expires = datetime.strptime(
        token_data["expires"], "%Y-%m-%d %H:%M:%S.%f"
    )  # timestamp example 2025-02-07 10:38:29.475885

    if expires < datetime.now():
        raise HTTPException(status_code=403, detail="Refresh token expired")

    else:
        access_token = create_access_token(data=token_data["user"])
        return {"access_token": access_token}
