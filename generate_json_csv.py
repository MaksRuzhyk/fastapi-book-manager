import json
import csv

books = [
    {"title": "Dune", "author": "Frank Herbert", "genre": "Fiction", "published_year": 1965},
    {"title": "Sapiens", "author": "Yuval Noah Harari", "genre": "History", "published_year": 2011},
    {"title": "A Brief History of Time", "author": "Stephen Hawking", "genre": "Science", "published_year": 1988},
]


with open("books.json", "w", encoding="utf-8") as f:
    json.dump(books, f, indent=2, ensure_ascii=False)


with open("books.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "author", "genre", "published_year"])
    writer.writeheader()
    writer.writerows(books)

print("✅ Файли books.json і books.csv створені у корені проєкту")