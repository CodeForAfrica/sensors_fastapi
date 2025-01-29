from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.utils import decode_token


class BaseTokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        auth_scheme_params = await super().__call__(request)

        print(auth_scheme_params.scheme)
        token = auth_scheme_params.credentials
        print(token)
        # valid_token = self.validate_token(token)
        valid_token = decode_token(token)
        if not valid_token:
            raise HTTPException(status_code=403, detail="Invalid or expired token")

        self.verify_token(token)

        return valid_token

    # def validate_token(self, token: str) -> bool:
    #     token_data = decode_token(token)
    #     return True if token_data is not None else False

    def verify_token(self, token_data):
        raise NotImplementedError("Method override in child class required")


class AccessTokenBearer(BaseTokenBearer):
    def verify_token(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=403, detail="Please provide an access token"
            )


class RefreshTokenBearer(BaseTokenBearer):
    def verify_token(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=403, detail="Please provide a refresh token"
            )
