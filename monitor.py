import requests
import sqlite3
import time

def monitor_api():
    conn = sqlite3.connect("data/api_logs.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    apis = cursor.execute("SELECT * FROM apis").fetchall()

    for api in apis:
        url = api["url"]

        try:
            start = time.time()
            res = requests.get(
                url,
                timeout=5,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response_time = round(time.time() - start, 3)
            status = res.status_code
        except:
            response_time = -1
            status = 500

        cursor.execute(
            "INSERT INTO logs (api_url, status_code, response_time) VALUES (?, ?, ?)",
            (url, status, response_time)
        )

    conn.commit()
    conn.close()