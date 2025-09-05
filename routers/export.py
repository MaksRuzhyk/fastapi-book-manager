from typing import Optional, Literal
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
import csv, io

from app.db import conn, get_dict_cursor
from app.books import Genre, row_to_out

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/export")
def export_books(
    export_format: Literal["json", "csv"] = Query(
        "json",
        alias="format",
        description="Формат експорту"
    ),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    genre: Optional[Genre] = Query(None),
):
    where, args = [], []
    if genre:
        where.append("b.genre = %s")
        args.append(genre.value)

    sql = f"""
        SELECT b.id, b.title, a.name AS author, b.genre::text AS genre, b.published_year
        FROM books b
        JOIN authors a ON a.id = b.author_id
        {"WHERE " + " AND ".join(where) if where else ""}
        ORDER BY b.title
        LIMIT %s OFFSET %s
    """
    args += [limit, offset]

    with conn() as c, get_dict_cursor(c) as cur:
        cur.execute(sql, args)
        rows = cur.fetchall()

    if export_format == "json":
        return JSONResponse(content=[row_to_out(r).model_dump() for r in rows])


    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["id", "title", "author", "genre", "published_year"])
    writer.writeheader()
    for r in rows:
        writer.writerow(row_to_out(r).model_dump())
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="books.csv"'},
    )