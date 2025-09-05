from typing import Any, Dict, List, Tuple
import json
import csv
import io
from psycopg.errors import UniqueViolation

from app.db import conn, get_dict_cursor
from app.books import BookIn, get_or_create_author

def parse_upload(filename: str, content_type: str | None, raw: bytes) -> List[Dict[str, Any]]:
    name = (filename or "").lower()
    is_json = ("json" in name) or (content_type == "application/json")
    is_csv = ("csv" in name) or (content_type in {"text/csv", "application/csv"})

    if not (is_json or is_csv):
        raise ValueError("Підтримуються лише JSON або CSV")

    if is_json:
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Некоректний JSON: {e}")

        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]
        if isinstance(data, list):
            return data
        raise ValueError("JSON має бути масивом об'єктів або {'items': [...]}")

    try:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        expected = {"title", "author", "genre", "published_year"}
        got = set(map(str.lower, reader.fieldnames or []))
        if got != expected:
            raise ValueError("CSV заголовок має бути: title,author,genre,published_year")

        items: List[Dict[str, Any]] = []
        for idx, row in enumerate(reader, start=2):
            items.append({
                "title": row.get("title"),
                "author": row.get("author"),
                "genre": row.get("genre"),
                "published_year": int(row.get("published_year") or 0),
                "_row": idx,
            })
        return items
    except Exception as e:
        raise ValueError(f"Некоректний CSV: {e}")

def import_books_items(items: List[Dict[str, Any]], user_id: int) -> Tuple[int, int, List[Dict[str, Any]]]:
    created = 0
    skipped = 0
    errors: List[Dict[str, Any]] = []

    with conn() as c, get_dict_cursor(c) as cur:
        for i, raw_item in enumerate(items, start=1):
            row_no = raw_item.pop("_row", i)

            try:
                item = BookIn(**raw_item)
            except Exception as e:
                errors.append({"row": row_no, "error": str(e)})
                skipped += 1
                continue

            try:
                author_id = get_or_create_author(cur, item.author)
                cur.execute(
                    """INSERT INTO books(title, author_id, genre, published_year, owner_id)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (item.title, author_id, item.genre.value, item.published_year, user_id),
                )
                created += 1
            except UniqueViolation:
                skipped += 1
                errors.append({"row": row_no, "error": "duplicate (already exists)"})
            except Exception as e:
                skipped += 1
                errors.append({"row": row_no, "error": f"db error: {e}"})

    return created, skipped, errors