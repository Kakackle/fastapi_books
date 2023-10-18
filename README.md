# FastAPI API with users, search history and info on programming books by amazon reviews etc

Important endpoints:

* /books/ - get books from dataset with filtering by query params, eg.

curl -X 'GET' \
  'http://127.0.0.1:8000/books/?title=handbook&desc=%something&ordering=publish_date' \
  -H 'accept: application/json'


* /users/ - get all users

* /register/ - register new user, returns a token value

* /login/ - login with email and password, returns a token value

* /books/{book_id}/favourite - add book specified by book id to user-tied favourite books

will only work if authorized

how to authorize? with an Authorization header:

eg.
curl -X 'POST' \
  'http://127.0.0.1:8000/books/1350/favourite' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjE1LCJleHAiOjE2OTc2NTc2Nzh9.i0KgghLZnhWiIt5DzROxbTF42Qh9QiSSjdNqzgmS_90' \
  -d ''

with a postgres database

Current models:

User
Book
History
Favourites

launch app

launch app
```
python -m uvicorn main:app --reload
```

docs on BASE_URL/docs


migrate model changes

1. make changes
2. `alembic revision --autogenerate -m "message"`
3.  `alembic upgrade head`


postgresql db on localhost:5432

db: ksiazki

server/user: postgres

password: postgres


===================


more info on extending the documentation: https://fastapi.tiangolo.com/tutorial/metadata/


====================

some sql commands for migrating the csv set into postgres

```
-- CREATE TABLE books (
-- 	id SERIAL,
-- 	title VARCHAR(250),
-- 	description TEXT,
-- 	author VARCHAR(100),
-- 	isbn10 VARCHAR(10),
-- 	isbn13 VARCHAR(15),
-- 	publish_date DATE,
--  edition INTEGER,
-- 	best_seller BOOL,
-- 	top_rated BOOL,
-- 	rating NUMERIC(2,1),
-- 	review_count INTEGER,
-- 	price NUMERIC(5,2),
-- 	PRIMARY KEY (id)
-- )

COPY books(title, description, author, isbn10, isbn13, publish_date, edition, best_seller, top_rated, rating, review_count, price)
FROM 'C:\Users\User\Desktop\books2.csv'
DELIMITER ','
CSV HEADER;

-- ALTER TABLE books
-- ADD COLUMN edition INTEGER

ALTER TABLE books
ALTER COLUMN isbn13 TYPE
VARCHAR(20)
```
