import sqlite3

def fix_database():
    conn = sqlite3.connect("data/api_logs.db")
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE logs ADD COLUMN error_type TEXT")
        print("Column added successfully")
    except Exception as e:
        print("Column already exists or error:", e)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_database()