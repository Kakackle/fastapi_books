from fastapi import APIRouter

router = APIRouter(tags=["favourite"])

from resources.db import database
from resources.tables import favourites, books, users

# @router.post("")