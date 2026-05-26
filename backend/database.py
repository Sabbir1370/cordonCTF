# backend/database.py
import pymysql
from pymysql.cursors import DictCursor
from .config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

def get_connection():
    """Return a new database connection (remember to close it)."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=DictCursor,
        autocommit=True
    )

def get_db():
    """FastAPI dependency that yields a cursor and closes the connection."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
    finally:
        conn.close()