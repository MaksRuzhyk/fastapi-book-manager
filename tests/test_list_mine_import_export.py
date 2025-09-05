import io, json
from fastapi.testclient import TestClient

B1 = {"title":"Dune","author":"Frank Herbert","genre":"Fiction","published_year":1965}
B2 = {"title":"Sapiens","author":"Yuval Noah Harari","genre":"History","published_year":2011}
B3 = {"title":"A Brief History of Time","author":"Stephen Hawking","genre":"Science","published_year":1988}

def seed_books(client: TestClient, headers):
    for b in (B1, B2, B3):
        r = client.post("/books", headers=headers, json=b)
        assert r.status_code == 200

def test_public_filters_and_mine(client: TestClient, auth_headers, other_headers):
    seed_books(client, auth_headers)
    client.post("/books", headers=other_headers, json={
        "title":"Metallica","author":"James","genre":"History","published_year":2000
    })

    # публічний список
    r = client.get("/books?search=History")
    assert r.status_code == 200
    assert any(x["title"] == "A Brief History of Time" for x in r.json())

    # mine
    r = client.get("/books/by-owner", headers=auth_headers)
    assert r.status_code == 200
    ids = {x["title"] for x in r.json()}
    assert ids == {"Dune", "Sapiens", "A Brief History of Time"}

def test_import_json_and_csv(client: TestClient, auth_headers):
    # JSON import
    data = json.dumps([B1, B2]).encode("utf-8")
    files = {"file": ("books.json", data, "application/json")}
    r = client.post("/books/import", headers=auth_headers, files=files)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["created"] == 2

    # CSV import
    csv_text = (
        "title,author,genre,published_year\n"
        "Dune,Frank Herbert,Fiction,1965\n"
        "A Brief History of Time,Stephen Hawking,Science,1988\n"
    ).encode("utf-8")
    files = {"file": ("books.csv", csv_text, "text/csv")}
    r = client.post("/books/import", headers=auth_headers, files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["created"] == 1
    assert body["skipped"] >= 1

def test_export_json_and_csv(client: TestClient, auth_headers):
    for b in (B1, B2):
        client.post("/books", headers=auth_headers, json=b)

    # JSON export
    r = client.get("/books/export?format=json&genre=History")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    data = r.json()
    assert all(x["genre"] == "History" for x in data)

    # CSV export
    r = client.get("/books/export?format=csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "Content-Disposition" in r.headers
    assert "books.csv" in r.headers["Content-Disposition"]
    text = r.text.splitlines()
    assert text[0] == "id,title,author,genre,published_year"