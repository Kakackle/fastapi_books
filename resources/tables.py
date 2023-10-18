from .db import metadata
import sqlalchemy

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), nullable=True),
)

# class Users(Base):
#     __tablename__ = "users",
#     id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True),
#     username = sqlalchemy.Column(sqlalchemy.String),
#     password = sqlalchemy.Column(sqlalchemy.String),
#     email = sqlalchemy.Column(sqlalchemy.String),
#     created_at = sqlalchemy.Column(sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), nullable=True),

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

favourites = sqlalchemy.Table(
    "favourites",
    metadata,
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("book_id", sqlalchemy.ForeignKey("books.id"), nullable=False),
    sqlalchemy.Column("date_added", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
)

history = sqlalchemy.Table(
    "history",
    metadata,
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("search_term", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("date_searched", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    # __table_args__ = {'extend_existing': True},
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
)