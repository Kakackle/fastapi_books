import databases
import sqlalchemy
from fastapi import FastAPI, Request

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


# many to many example
groups = sqlalchemy.Table(
    "groups",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    # sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
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

# start app
app = FastAPI()

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

@app.post("/users/")
async def create_user(request: Request):
    data = await request.json()
    # query = users.insert().values(**data)
    # query = users.insert().values(username="test_user", password="password",
    #                                email="test@test.com")
    query = users.insert().values(username=data["username"],
                                   password=data["password"],
                                   email=data["email"])
    last_record_id = await database.execute(query)
    return {"id": last_record_id}

@app.post("/posts/")
async def create_user(request: Request):
    data = await request.json()
    query = posts.insert().values(**data)
    # query = users.insert().values(username="test_user", password="password",
    #                                email="test@test.com")
    # query = users.insert().values(username=data["username"],
    #                                password=data["password"],
    #                                email=data["email"])
    last_record_id = await database.execute(query)
    return {"id": last_record_id}