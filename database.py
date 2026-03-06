import sqlite3
import os

# create data folder if not exists
os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/api_logs.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_url TEXT,
    status_code INTEGER,
    response_time REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database and table created successfully")