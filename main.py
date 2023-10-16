from datetime import datetime
from typing import Optional
import databases
import sqlalchemy
from fastapi import FastAPI, Request
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM
from pydantic import BaseModel, ValidationError, field_validator, validate_email, validator
from email_validator import EmailNotValidError
from passlib.context import CryptContext

from decouple import config

DATABASE_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@localhost:5432/ksiazki"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# test tables
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String),
    # sqlalchemy.Column("test_field", sqlalchemy.Integer)
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), nullable=True)
)

# one to many relationship example - one user, many posts
posts = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("content", sqlalchemy.String),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

class PermissionEnum(Enum):
    admin = "admin"
    basic = "basic"

# many to many example
groups = sqlalchemy.Table(
    "groups",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    # sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
    # sqlalchemy.Column("permission", ENUM(PermissionEnum), nullable=False)
    # sqlalchemy.Column("permission", sqlalchemy.Enum(PermissionEnum), nullable=False)
)

groups_users = sqlalchemy.Table(
    "groups_users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("group_id", sqlalchemy.ForeignKey("groups.id"), nullable=False)
)

# ============= without alembic migrations ==============

# engine = sqlalchemy.create_engine(DATABASE_URL)
# metadata.create_all(engine)

# with alembic
# in terminal: alembic revision --autogenerate -m "message"
# -> alembic upgrade head

# class EmailField(str):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v) -> str:
#         try:
#             validate_email(v)
#             return v
#         except EmailNotValidError:
#             raise ValueError("Invalid email format")

class BaseUser(BaseModel):
    username: str
    # email: EmailField
    email: str

    @field_validator("email")
    @classmethod
    def validate_e_mail(cls, v):
        try:
            validate_email(v)
            return v
        except ValidationError:
            raise ValueError("Invalid email format")


# sign up schema, extends base user schema
class UserSignIn(BaseUser):
    password: str
    # created_at: datetime

# just for display purposes
class UserSignOut(BaseUser):
    created_at: Optional[datetime]
    # test_field = int

# start app
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# on startup
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get('/users/')
async def get_all_users():
    query = users.select()
    return await database.fetch_all(query)

# @app.post("/users/")
# async def create_user(request: Request):
#     data = await request.json()
#     # query = users.insert().values(**data)
#     # query = users.insert().values(username="test_user", password="password",
#     #                                email="test@test.com")
#     query = users.insert().values(username=data["username"],
#                                    password=data["password"],
#                                    email=data["email"])
#     last_record_id = await database.execute(query)
#     return {"id": last_record_id}

@app.post("/register/", response_model=UserSignOut)
async def create_user(user: UserSignIn):
    user.password = pwd_context.hash(user.password)
    query = users.insert().values(**user.model_dump())
    user_id = await database.execute(query)
    created_user = await database.fetch_one(users.select().where(users.c.id == user_id))
    return created_user

@app.post("/posts/")
async def create_post(request: Request):
    data = await request.json()
    query = posts.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}