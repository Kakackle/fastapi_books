from typing import Annotated
from fastapi import APIRouter, Depends
from asyncpg import UniqueViolationError
from fastapi import HTTPException
import jwt
from decouple import config

router = APIRouter(tags=["user"])

from resources.tables import users
from resources.schemas import (UserSignUpIn, UserSignUpOut,
                                UserLoginIn, UserLoginOut,
                                BaseUser)
from resources.db import database
from resources.auth import pwd_context, create_access_token, oauth2_scheme

@router.get('/users/')
async def get_all_users():
    query = users.select()
    return await database.fetch_all(query)

# @app.post("/register/", response_model=UserSignOut)
@router.post("/register/")
async def create_user(user: UserSignUpIn) -> UserSignUpOut:
    user.password = pwd_context.hash(user.password)
    query = users.insert().values(**user.model_dump())
    try:
        user_id = await database.execute(query)
    except UniqueViolationError:
        raise HTTPException(400, "User with this email already exists")
    created_user = await database.fetch_one(users.select().where(users.c.id == user_id))
    token = create_access_token(created_user)
    return {"email": created_user.email,
            "created_at":created_user.created_at,
            "token": token}

@router.post("/login/")
async def login(user: UserLoginIn) -> UserLoginOut:
    user_data = user.model_dump()
    user_do = await database.fetch_one(
        users.select().where(users.c.email == user_data["email"])
    )
    if not user_do:
        raise HTTPException(400, "Wrong email or password")
    elif not pwd_context.verify(user_data["password"], user_do["password"]):
        raise HTTPException(400, "Wrong email or password")
    return {"token": create_access_token(user_do)}

async def decode_token(token):
    payload = jwt.decode(jwt = token, key=config("JWT_SECRET"), algorithms=["HS256"])
    user = await database.fetch_one(users.select().where(users.c.id == payload["sub"]))
    return user

async def get_current_user(token: Annotated[bytes, Depends(oauth2_scheme)]):
    # print("token", token)
    token_proper = jwt.encode(token, config("JWT_SECRET"), algorithm="HS256")
    user = await decode_token(token_proper)
    return user

@router.get('/users/current')
async def read_current_user(current_user: Annotated[BaseUser, Depends(get_current_user)]):
    return current_user

# @router.get('/favourites/')
# async def get_favourites():
#     user = await read_current_user()
