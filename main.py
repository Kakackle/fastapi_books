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


# extra app documentation
description = """
*CS Books API*
An interactive API implementation of the "Amazon Books details for computer science" dataset
to be found at: https://www.kaggle.com/datasets/uzair01/amazon-books/

Essentially a dataset of recent books on differenct CS subjects with info on average rating, whether it achieved bestseller status, a short description etc

* with some data cleaning done
* an authenticated user system
* a save to favourites system
* a search history for logged users system

using oauth2 with jwt token authentication of type "bearer"
"""
summary="CS Books API summary"
version = "0.1.5"

tags_metadata = [
    {
        "name": "user",
        "description": "Operations relating to users, auth included"
    },
    {
        "name": "books",
        "description": "Operations relating to books"
    },
    {
        "name": "favourites",
        "description": "Operations relating to the favourites system"
    },
    {
        "name": "history",
        "description": "Operations relating to the history system"
    },
]

# start app
app = FastAPI(
    title = "CS Books API",
    description=description,
    summary=summary,
    version=version,
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Kakackle",
        "url": "https://github.com/Kakackle"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
)
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