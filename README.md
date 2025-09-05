#  Book Management System (FastAPI + PostgreSQL)

## Опис
Це REST API для управління книгами. Підтримує CRUD, пошук, фільтри, сортування, імпорт/експорт JSON/CSV, аутентифікацію через JWT.

---

## Вимоги
- Python 3.12+
- PostgreSQL 14+
- pip, venv

---
## Аутентифікація

`POST /auth/signup` → реєстрація

`POST /auth/token` → отримання JWT

`Authorization: Bearer <token>` у запитах до захищених роутів

---
## Основні ендпоїнти

- `GET /books` — список книг (з фільтрацією та пагінацією)


- `POST /books` — створення книги (авторизований користувач)


- `GET /books/{id}` — отримання книги за ID


- `PUT /books/{id}` — оновлення книги (тільки власник)


- `DELETE /books/{id}` — видалення книги (тільки власник)


- `POST /books/import` — імпорт JSON/CSV


- `GET /books/export` — експорт JSON/CSV


- `GET /books/by-owner` — книги поточного користувача

---
##  Установка
```bash
git clone <repo_url>
cd FastAPI_Project
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```
---
## Налаштування БД

- Створіть файл `.env` на основі `.env.example`


- Запустіть ініціалізацію:
```
python init_db.py
```
---

## Запуск сервера

```
python main.py

#або

uvicorn main:app --reload
```

---
## Тести

```
pytest -v
```


