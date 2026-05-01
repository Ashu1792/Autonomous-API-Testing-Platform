from app.models.database import get_db

def test_database_connection():
    conn = get_db()
    assert conn is not None
    conn.close()