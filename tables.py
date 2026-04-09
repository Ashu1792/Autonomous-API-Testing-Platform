import sqlite3

conn = sqlite3.connect("data/api_logs.db")
cursor = conn.cursor()

# APIs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS apis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE
)
""")

# Logs table (IMPORTANT)
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_id INTEGER,
    status TEXT,
    response_time REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(api_id) REFERENCES apis(id)
)
""")

conn.commit()
conn.close()

print("Tables created successfully!")