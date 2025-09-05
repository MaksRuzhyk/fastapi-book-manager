import re
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, field_validator




CURRENT_YEAR = datetime.now().year
TITLE_RE  = re.compile(r"^[A-Za-zА-Яа-яІіЇїЄєҐґ0-9\s\"']+$")
AUTHOR_RE = re.compile(r"^[A-Za-zА-Яа-яІіЇїЄєҐґ\s]+$")

class Genre(str, Enum):
    fiction    = "Fiction"
    nonfiction = "Non-Fiction"
    science    = "Science"
    history    = "History"

class BookIn(BaseModel):
    title: str = Field(..., min_length=1, description="Лише букви/цифри/лапки")
    author: str = Field(..., min_length=1, description="Лише букви")
    genre: Genre
    published_year: int = Field(..., ge=1800, le=CURRENT_YEAR,
                                description=f"Рік від 1800 до {CURRENT_YEAR}")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str):
        v = v.strip()
        if not TITLE_RE.match(v):
            raise ValueError("title може містити тільки букви, цифри та лапки")
        return v

    @field_validator("author")
    @classmethod
    def validate_author(cls, v: str):
        v = v.strip()
        if not AUTHOR_RE.match(v):
            raise ValueError("author може містити тільки букви")
        return v

class BookOut(BookIn):
    id: int

def get_or_create_author(cur, name: str) -> int:
    cur.execute("SELECT id FROM authors WHERE name=%s", (name,))
    r = cur.fetchone()
    if r:
        return r["id"]
    cur.execute("INSERT INTO authors(name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()["id"]

def row_to_out(r) -> BookOut:
    return BookOut(**r)




