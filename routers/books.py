from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from sqlalchemy import desc as descending

from resources.schemas import BaseUser, BaseFav, BaseHistory
from .users import get_current_user
import sqlalchemy

router = APIRouter(tags=["books"])

from resources.db import database
from resources.tables import books, users, favourites, history
from resources.auth import oauth2_scheme

# @router.get("/books/", dependencies=[Depends(oauth2_scheme)])
@router.get("/books_head/")
async def get_books_head():
    query = books.select().limit(5)
    return await database.fetch_all(query)

@router.get("/books/", description="Get books with filtering and ordering through query params, without saving to user's history of searches")
async def get_books(title: str = "%", desc: str = "%",
                    author: str = "%", rating_gte: float = 0.0,
                    review_count_gte: int = 0, price_gte: float = 0.0,
                    price_lte: float = 999.99, edition_gte: int = 1,
                    ordering: str = Query("publish_date", enum=["publish_date", "rating", "review_count", "price", "title"])):
    query = books.select().where(
        (books.c.title.ilike(f"%{title}%")) &
        (books.c.description.ilike(f"%{desc}%")) &
        (books.c.author.ilike(f"%{author}%")) &
        (books.c.rating >= rating_gte) &
        (books.c.review_count >= review_count_gte) &
        (books.c.price >= price_gte) &
        (books.c.price <= price_lte) &
        (books.c.edition >= edition_gte)
        ).order_by(descending(ordering))
    # print("query: ", str(query))
    return await database.fetch_all(query)

# books retrieve endpoint with history saving
@router.get("/books/save", description="Get books with filtering and ordering through query params, WITH saving to user's history of searches",
            tags=["books", "history"])
async def get_books_save(
                    current_user:Annotated[BaseUser, Depends(get_current_user)],
                    title: str = "%", desc: str = "%",
                    author: str = "%", rating_gte: float = 0.0,
                    review_count_gte: int = 0, price_gte: float = 0.0,
                    price_lte: float = 999.99, edition_gte: int = 1,):
    query = books.select().where(
        (books.c.title.ilike(f"%{title}%")) &
        (books.c.description.ilike(f"%{desc}%")) &
        (books.c.author.ilike(f"%{author}%")) &
        (books.c.rating >= rating_gte) &
        (books.c.review_count >= review_count_gte) &
        (books.c.price >= price_gte) &
        (books.c.price <= price_lte) &
        (books.c.edition >= edition_gte)
        )
    
    query_string = f"?title={title}&description={desc}&author={author}\
&rating_gte={rating_gte}&review_count_gre={review_count_gte}\
&price_gte={price_gte}&price_lte={price_lte}&edition_gte={edition_gte}"
    
    fav_hist = BaseHistory(user_id=current_user.id,
                           search_term=query_string,
                           date_searched=datetime.now())
    
    history_query = history.insert().values(**fav_hist.model_dump())
    try:
        his_id = await database.execute(history_query)
    except Exception as e:
        raise HTTPException(400, f"something went wrong: {e}")
    created_his = await database.fetch_one(history.select().where(history.c.id == his_id))

    return await database.fetch_all(query)

@router.get("/books/{book_id}")
async def get_book(book_id:int):
    query = books.select().where(books.c.id == book_id)
    return await database.fetch_one(query)

@router.post("/books/{book_id}/favourite", description="add book to user's favourites",
             tags=["books", "favourites"])
async def add_to_favourites(book_id:int, current_user:Annotated[BaseUser, Depends(get_current_user)]):
    user_id = current_user.id
    fav_data = BaseFav(user_id=user_id, book_id=book_id, date_added=datetime.now())
    query = favourites.insert().values(**fav_data.model_dump())
    try:
        fav_id = await database.execute(query)
    except Exception as e:
        raise HTTPException(400, f"something went wrong: {e}")
    created_fav = await database.fetch_one(favourites.select().where(favourites.c.id == fav_id))
    return {created_fav}
    
@router.get("/favourites/", tags=["favourites"])
async def get_favourites(current_user: Annotated[BaseUser, Depends(get_current_user)]):
    query = favourites.select().where(favourites.c.user_id == current_user.id)
    favs = await database.fetch_all(query)
    return favs

@router.get("/favourites/{user_id}", tags=["favourites"])
async def get_user_favourites(user_id:int):
    query = favourites.select().where(favourites.c.user_id == user_id)
    favs = await database.fetch_all(query)
    return favs


@router.get("/history/", tags=["history"])
async def get_history(current_user: Annotated[BaseUser, Depends(get_current_user)]):
    query = history.select().where(history.c.user_id == current_user.id)
    history_data = await database.fetch_all(query)
    return history_data