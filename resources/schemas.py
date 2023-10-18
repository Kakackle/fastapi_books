from pydantic import BaseModel, ValidationError, field_validator, validate_email, validator
from datetime import datetime, timedelta
from typing import Optional

class BaseUser(BaseModel):
    id: int
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
class UserSignUpIn(BaseUser):
    password: str
    # created_at: datetime

# just for display purposes
class UserSignUpOut(BaseModel):
    email: str
    created_at: Optional[datetime]
    token: str
    # test_field = int

class UserLoginIn(BaseModel):
    email: str
    password: str

class UserLoginOut(BaseModel):
    token: str

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

class BaseFavourite(BaseModel):
    user_id: int
    book_id: int
    date_added: datetime

class BaseHistory(BaseModel):
    user_id: int
    search_term: str
    date_searched: datetime

class BaseFav(BaseModel):
    user_id: int
    book_id: int
    date_added: datetime