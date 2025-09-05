from fastapi.testclient import TestClient

BOOK = {"title": "Moby-Dick", "author": "Herman Melwille", "genre": "Fiction", "published_year": 1851}

def test_public_list_empty_ok(client: TestClient):
    r = client.get("/books")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert r.json() == []

def test_crud_and_permissions(client: TestClient, auth_headers, other_headers):
    # create
    r = client.post("/books", headers=auth_headers, json=BOOK)
    assert r.status_code == 200, r.text
    book = r.json()
    bid = book["id"]
    assert book["title"] == "Moby-Dick"

    # get by id
    r = client.get(f"/books/id/{bid}")
    assert r.status_code == 200
    assert r.json()["author"] == "Herman Melwille"
    # update своїм токеном
    changed = {**BOOK, "published_year": 1966}
    r = client.put(f"/books/{bid}", headers=auth_headers, json=changed)
    assert r.status_code == 200
    assert r.json()["published_year"] == 1966

    # update чужим токеном → 403
    r = client.put(f"/books/{bid}", headers=other_headers, json=changed)
    assert r.status_code == 403

    # delete чужим токеном → 403
    r = client.delete(f"/books/{bid}", headers=other_headers)
    assert r.status_code == 403

    # delete своїм токеном
    r = client.delete(f"/books/{bid}", headers=auth_headers)
    assert r.status_code == 200

    # get by id → 404
    r = client.get(f"/books/id/{bid}")
    assert r.status_code == 404

def test_duplicate_conflict(client: TestClient, auth_headers):
    r1 = client.post("/books", headers=auth_headers, json=BOOK)
    assert r1.status_code == 200
    r2 = client.post("/books", headers=auth_headers, json=BOOK)
    assert r2.status_code == 409