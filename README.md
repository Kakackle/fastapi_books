# FastAPI API with users, search history and info on programming books by amazon reviews etc

launch app

launch app
```
python -m uvicorn main:app --reload
```

docs on BASE_URL/docs


migrate model changes

1. make changes
2. `alembic revision --autogenerate -m "message"`
3.  alembic upgrade head


Currently planned models:

User
Book
History
Favourites

postgresql db on localhost:5432

db: ksiazki

server/user: postgres

password: postgres


====================

some sql commands for migrating the csv set into postgres

```
-- CREATE TABLE books (
-- 	id SERIAL,
-- 	title VARCHAR(250),
-- 	description TEXT,
-- 	author VARCHAR(100),
-- 	isbn10 VARCHAR(10),
-- 	isbn13 VARCHAR(14),
-- 	publish_date DATE,
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
