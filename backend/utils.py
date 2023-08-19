from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

import os
import time
from typing import Dict, Union, Any

import jwt
from dotenv import load_dotenv

from exception import ForbiddenException

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print(JWT_SECRET, JWT_ALGORITHM)


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def token_response(token: str):
    return {
        "access_token": token
    }


def create_access_token(subject: Union[str, Any]) -> Dict[str, str]:
    payload = {
        "sub": str(subject),
        "expires": time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60,

    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decode_token(token: str) -> Dict[str, str]:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e:
        return {}


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise ForbiddenException("Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise ForbiddenException("Invalid token or expired token.")
            return credentials.credentials
        else:
            raise ForbiddenException("Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decode_token(jwtoken)
        except Exception:
            payload = None

        return payload is not None

    # get current user
