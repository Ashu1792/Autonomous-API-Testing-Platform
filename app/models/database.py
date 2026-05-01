import sqlite3
import os

DB_PATH = "data/api_logs.db"


# ---------------- CREATE CONNECTION ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- INIT DATABASE ----------------
def init_db():
    # create data folder if not exists
    os.makedirs("data", exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    # ---------------- USERS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # ---------------- APIS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE
    )
    """)

    # ---------------- LOGS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_url TEXT,
        status_code INTEGER,
        response_time REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        error_type TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully")