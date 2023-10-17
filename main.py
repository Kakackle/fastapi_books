from datetime import datetime, timedelta
from typing import Optional
import databases
import jwt
import sqlalchemy
from fastapi import Depends, FastAPI, HTTPException, Request
from starlette.requests import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), nullable=True),
)

books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("title", sqlalchemy.VARCHAR(250), server_default="untitled"),
    sqlalchemy.Column("description", sqlalchemy.TEXT),
    sqlalchemy.Column("author", sqlalchemy.VARCHAR(100)),
    sqlalchemy.Column("isbn10", sqlalchemy.VARCHAR(10)),
    sqlalchemy.Column("isbn13", sqlalchemy.VARCHAR(16)),
    sqlalchemy.Column("publish_date", sqlalchemy.DATE),
    sqlalchemy.Column("edition", sqlalchemy.INTEGER, server_default="0"),
    sqlalchemy.Column("best_seller", sqlalchemy.BOOLEAN, server_default="no"),
    sqlalchemy.Column("top_rated", sqlalchemy.BOOLEAN, server_default="no"),
    sqlalchemy.Column("rating", sqlalchemy.Numeric(precision=2, scale=1), server_default="0"),
    sqlalchemy.Column("review_count", sqlalchemy.INTEGER, server_default="0"),
    sqlalchemy.Column("price", sqlalchemy.Numeric(precision=5, scale=2), server_default="99"),
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
)

# ============= without alembic migrations ==============

# engine = sqlalchemy.create_engine(DATABASE_URL)
# metadata.create_all(engine)

# with alembic
# in terminal: alembic revision --autogenerate -m "message"
# -> alembic upgrade head

class BaseUser(BaseModel):
    username: str
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

class BasePost(BaseModel):
    title: str
    content: str
    user_id: int


class BaseBook(BaseModel):
    id: int
    title: str
    description: str | None = None
    author: str | None = None
    isbn10: str | None = None
    isbn13: str | None = None
    publish_date: datetime | None = None
    edition: int | None = None
    best_seller: bool | None = None
    top_rated: bool | None = None
    rating: float | None = None
    review_count: int | None = None
    price: float | None = None

# start app
app = FastAPI()
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

# @app.post("/register/", response_model=UserSignOut)
@app.post("/register/")
async def create_user(user: UserSignIn):
    user.password = pwd_context.hash(user.password)
    query = users.insert().values(**user.model_dump())
    user_id = await database.execute(query)
    created_user = await database.fetch_one(users.select().where(users.c.id == user_id))
    token = create_access_token(created_user)
    return {"token": token}

@app.get("/books/")
async def get_5_books():
    query = books.select().limit(5)
    return await database.fetch_all(query)

# z tokenem
# @app.get("/posts/", dependencies=[Depends(oauth2_scheme)])
# async def get_all_posts():
#     return await database.fetch_all(posts.select())