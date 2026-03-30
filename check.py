import sqlite3

conn = sqlite3.connect("data/api_logs.db")
cursor = conn.cursor()

cursor.execute("SELECT status_code, COUNT(*) FROM logs GROUP BY status_code")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()