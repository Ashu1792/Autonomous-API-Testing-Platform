import time
import requests
from app.models.database import get_db

def monitor_apis():
    while True:
        conn = get_db()
        apis = conn.execute("SELECT url FROM apis").fetchall()

        for api in apis:
            url = api["url"]

            start = time.time()
            try:
                res = requests.get(url, timeout=5)
                status = res.status_code
            except:
                status = 500

            response_time = round(time.time() - start, 3)

            conn.execute("""
                INSERT INTO logs (api_url, status_code, response_time)
                VALUES (?, ?, ?)
            """, (url, status, response_time))

        conn.commit()
        conn.close()

        print("🔄 Auto monitoring running...")

        time.sleep(10)