from decouple import config
from datetime import datetime, timedelta
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from typing import Optional
from starlette.requests import Request
from fastapi import HTTPException
import jwt
from .db import database
from .tables import users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CustomHTTPBearer(HTTPBearer):
    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)

        try:
            payload = jwt.decode(res.credentials, config("JWT_SECRET"), algorithms=["HS256"])
            user = await database.fetch_one(users.select().where(users.c.id == payload["sub"]))
            # global request state, available in the whole app
            request.state.user = user
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token is expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")


# obiekt do obslugi customowej definicji zachowania sprawdzania bearera itd
oauth2_scheme = CustomHTTPBearer()

def create_access_token(user):
    try:
        payload = {"sub": user.id, "exp": datetime.utcnow() + timedelta(minutes=120)}
        return jwt.encode(payload, config("JWT_SECRET"), algorithm="HS256")
    except Exception as ex:
        raise ex

# def encode_token(user):
#         try:
#             payload = {
#                 "sub": user["id"],
#                 "exp": datetime.utcnow() + timedelta(minutes=120),
#             }
#             return jwt.encode(payload, config("SECRET_KEY"), algorithm="HS256")
#         except Exception as ex:
#             # Log the exception
#             raise ex