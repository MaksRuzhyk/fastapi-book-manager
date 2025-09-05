from fastapi import APIRouter, HTTPException, Query, Depends
from psycopg.errors import UniqueViolation
from typing import List, Optional

from app.books import BookIn, BookOut, Genre, get_or_create_author, row_to_out
from routers.auth import get_current_user_id
from app.db import conn, get_dict_cursor

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookOut)
def create_book(payload: BookIn, user_id: int = Depends(get_current_user_id)):
    try:
        with conn() as c, get_dict_cursor(c) as cur:
            author_id = get_or_create_author(cur, payload.author)
            cur.execute(
                """INSERT INTO books(title, author_id, genre, published_year, owner_id)
                   VALUES (%s,%s,%s,%s,%s)
                   RETURNING id, title, %s AS author, genre, published_year""",
                (payload.title, author_id, payload.genre.value, payload.published_year, user_id, payload.author),
            )
            return row_to_out(cur.fetchone())
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Книжка вже додана для цього автора і року")

@router.get("", response_model=List[BookOut])
def list_books(
                search: Optional[str] = Query(None, description="Пошук за назвою/автором."),
                author: Optional[str] = Query(None, description="Фільтр за автором."),
                genre: Optional[Genre] = Query(None, description="Фільтр за жанром."),
                year_from: Optional[int] = Query(None, ge=1800, description="Мінімальний рік."),
                year_to: Optional[int] = Query(None, ge=1800, description="Максимальний рік."),
                sort: str = Query("title", pattern="^(title|author|year)$", description="Сортування за полями."),
                order: str = Query("asc", pattern="^(asc|desc)$", description="Сортування за зростанням/спаданням."),
                limit: int = Query(20, ge=1, le=100, description="Максимальна кількість книг у відповіді (пагінація)."),
                offset: int = Query(0, ge=0, description="Кількість книг, які потрібно пропустити (зсув для пагінації)."),
                ):


    sort_map = {"title": "b.title", "author": "a.name", "year": "b.published_year"}
    order_kw = "ASC" if order == "asc" else "DESC"

    where = []
    args = []

    if search:
        where.append("(b.title ILIKE %s OR a.name ILIKE %s)")
        args += [f"%{search}%", f"%{search}%"]
    if author:
        where.append("a.name ILIKE %s")
        args.append(f"%{author}%")

    if genre:
        where.append("b.genre = %s")
        args.append(genre.value)

    if year_from is not None:
        where.append("b.published_year >= %s")
        args.append(year_from)

    if year_to is not None:
        where.append("b.published_year <= %s")
        args.append(year_to)


    sql = f"""
            SELECT b.id, b.title, a.name AS author, b.genre, b.published_year
            FROM books b
            JOIN authors a ON a.id = b.author_id
            {"WHERE " + " AND ".join(where) if where else ""}
            ORDER BY {sort_map[sort]} {order_kw}
            LIMIT %s OFFSET %s
        """
    args += [limit, offset]

    with conn() as c, get_dict_cursor(c) as cur:
        cur.execute(sql, args)
        rows = cur.fetchall()
        return [BookOut(**r) for r in rows]

@router.get("/by-owner", response_model=List[BookOut])
def list_my_books(user_id: int = Depends(get_current_user_id)):
    sql = """
        SELECT b.id, b.title, a.name AS author, b.genre, b.published_year
        FROM books b
        JOIN authors a ON a.id = b.author_id
        WHERE b.owner_id = %s
        ORDER BY b.title
    """
    with conn() as c, get_dict_cursor(c) as cur:
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        return [row_to_out(r) for r in rows]

@router.get("/id/{book_id}", response_model=BookOut)
def get_book(book_id: int):
    with conn() as c, get_dict_cursor(c) as cur:
        cur.execute(
            """SELECT b.id, b.title, a.name AS author, b.genre, b.published_year
               FROM books b
               JOIN authors a ON a.id = b.author_id
               WHERE b.id = %s""",
            (book_id,),
        )
        r = cur.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="Не знайдено")
        return row_to_out(r)

@router.put("/{book_id}", response_model=BookOut)
def update_book(book_id: int, payload: BookIn, user_id: int = Depends(get_current_user_id)):
    with conn() as c, get_dict_cursor(c) as cur:
        cur.execute("SELECT owner_id FROM books WHERE id=%s", (book_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Книга не знайдена.")

        if row['owner_id'] != user_id:
            raise HTTPException(status_code=403, detail="У доступі відмовлено.")

        author_id = get_or_create_author(cur, payload.author)
        cur.execute(
            """UPDATE books
               SET title=%s, author_id=%s, genre=%s, published_year=%s
               WHERE id=%s
               RETURNING id""",
            (payload.title, author_id, payload.genre.value, payload.published_year, book_id),
        )

        cur.execute(
            """SELECT b.id, b.title, a.name AS author, b.genre, b.published_year
               FROM books b
               JOIN authors a ON a.id = b.author_id
               WHERE b.id = %s""",
            (book_id,),
        )
        return row_to_out(cur.fetchone())

@router.delete("/{book_id}")
def delete_book(book_id: int, user_id: int = Depends(get_current_user_id)):
    with conn() as c, get_dict_cursor(c) as cur:
        cur.execute("SELECT owner_id FROM books WHERE id=%s", (book_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Книга не знайдена")
        if row["owner_id"] != user_id:
            raise HTTPException(status_code=403, detail="Немає доступу")

        cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
    return {"ok": True}