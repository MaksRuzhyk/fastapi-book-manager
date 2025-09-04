import os
import psycopg

from dotenv import load_dotenv

load_dotenv()

PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
DBNAME = os.getenv("DBNAME")
SCHEMA_FILE = os.getenv("SCHEMA_FILE")

def create_database():
    with psycopg.connect(host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DBNAME,))
            if cur.fetchone():
                print(f"[OK] Database '{DBNAME}' already exist")
            else:
                cur.execute(f'CREATE DATABASE "{DBNAME}";')
                print(f"[OK] Database '{DBNAME}' created")

def apply_schema():
    with open(SCHEMA_FILE, encoding="utf-8") as f:
        sql = f.read()
    with psycopg.connect(host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD,dbname=DBNAME, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    print(f"[OK] Schema from '{SCHEMA_FILE}' applied")

if __name__ == "__main__":
    create_database()
    apply_schema()