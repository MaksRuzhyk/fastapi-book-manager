import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
DBNAME = os.getenv("DBNAME")

def conn():
    return psycopg.connect(host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD,dbname=DBNAME, autocommit=True)

def get_dict_cursor(con):
    return con.cursor(row_factory=dict_row)