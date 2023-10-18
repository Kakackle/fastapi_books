from fastapi import Depends, FastAPI
from starlette.requests import Request
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from decouple import config

from resources.tables import users, books
from resources.schemas import UserSignUpIn, UserSignUpOut
from resources.db import database

from routers.books import router as book_router
from routers.users import router as user_router

from resources.db import metadata
metadata = metadata
# Base = declarative_base(metadata)

# ============= without alembic migrations ==============

# engine = sqlalchemy.create_engine(DATABASE_URL)
# metadata.create_all(engine)

# with alembic
# in terminal: alembic revision --autogenerate -m "message"
# -> alembic upgrade head


# start app
app = FastAPI()
app.include_router(user_router)
app.include_router(book_router)

# on startup
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()



# z tokenem
# @app.get("/posts/", dependencies=[Depends(oauth2_scheme)])
# async def get_all_posts():
#     return await database.fetch_all(posts.select())