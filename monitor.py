import requests
import sqlite3
import time

def monitor_api():
    conn = sqlite3.connect("data/api_logs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM apis")
    apis = cursor.fetchall()

    results = []

    for api in apis:
        api_id, url = api

        try:
            start = time.time()
            res = requests.get(url, timeout=5)
            response_time = round(time.time() - start, 3)

            status_code = res.status_code
            status = 200 if status_code == 200 else 500

        except:
            response_time = 0
            status = 500

        # ✅ Store logs (FIXED)
        cursor.execute("""
            INSERT INTO logs (api_url, status_code, response_time)
            VALUES (?, ?, ?)
        """, (url, status, response_time))

        # Return for dashboard
        results.append({
            "id": api_id,
            "api": url,
            "status": status,
            "response_time": response_time,
            "risk": "Low" if status == 200 else "High"
        })

    conn.commit()
    conn.close()

    return results