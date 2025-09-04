from app.db import conn, get_dict_cursor

with conn() as c, get_dict_cursor(c) as cur:
    cur.execute("SELECT 1 AS check;")
    print(cur.fetchone())