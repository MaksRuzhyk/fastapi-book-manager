import os
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient

# 1) Підвантажуємо .env і підміняємо БД на тестову
load_dotenv()
TEST_DB = os.getenv("DBNAME_TEST", "books_test")
os.environ["DBNAME"] = TEST_DB  # щоб app/db.py підключився до тестової бази

# 2) Ініціалізуємо БД (створення БД і накочення schema.sql)
from init_db import create_database, apply_schema
create_database()
apply_schema()

from main import app
from app.db import conn, get_dict_cursor


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    with conn() as c, get_dict_cursor(c) as cur:
        cur.execute("DELETE FROM books;")
        cur.execute("DELETE FROM authors;")
        cur.execute("DELETE FROM users;")
    yield

def _signup_and_token(client: TestClient, email="u1@example.com", pwd="Qa123456!"):
    client.post("/auth/signup", json={"email": email, "password": pwd})
    r = client.post("/auth/token", data={"username": email, "password": pwd})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]

@pytest.fixture
def auth_headers(client):
    token = _signup_and_token(client, email="user1@example.com")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def other_headers(client):
    token = _signup_and_token(client, email="user2@example.com")
    return {"Authorization": f"Bearer {token}"}