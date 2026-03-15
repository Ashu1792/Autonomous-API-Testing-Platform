from alert import send_alert
import requests
import sqlite3
import time

DB = "data/api_logs.db"

API_LIST = [
    "https://api.openweathermap.org/data/2.5/weather?q=London&appid=b452d4b9373592eb07f553041a7e5038",
    "https://jsonplaceholder.typicode.com/posts",
    "https://api.github.com/users/octocat"
]

def monitor_api():

    results = []

    try:
        with sqlite3.connect(DB, timeout=10, check_same_thread=False) as conn:

            conn.execute("PRAGMA journal_mode=WAL")
            cursor = conn.cursor()

            for url in API_LIST:

                start = time.time()

                try:
                    response = requests.get(url, timeout=5)

                    status = response.status_code
                    response_time = round(time.time() - start, 3)

                    if status != 200:
                        send_alert(url, status)

                except requests.exceptions.RequestException:

                    status = 500
                    response_time = 0
                    send_alert(url, status)

                risk = "LOW RISK" if status == 200 else "HIGH RISK"

                cursor.execute("""
                INSERT INTO logs(api_url,status_code,response_time,timestamp)
                VALUES (?,?,?,CURRENT_TIMESTAMP)
                """,(url,status,response_time))

                results.append({
                    "api": url.split("?")[0],
                    "status": status,
                    "response_time": response_time,
                    "risk": risk
                })

            conn.commit()

    except sqlite3.Error as e:
        print("Database error:", e)

    return results