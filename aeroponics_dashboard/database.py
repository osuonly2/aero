
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "aeroponics.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "username TEXT UNIQUE NOT NULL,"
            "password_hash TEXT NOT NULL"
            ")"
        )
        conn.commit()
