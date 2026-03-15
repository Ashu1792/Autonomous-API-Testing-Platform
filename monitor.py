from alert import send_alert
import requests
import sqlite3
import time

DB = "data/api_logs.db"

# Track consecutive failures (SRE alert escalation)
FAIL_COUNT = {}

API_LIST = [
    "https://api.openweathermap.org/data/2.5/weather?q=London&appid=b452d4b9373592eb07f553041a7e5038",
    "https://jsonplaceholder.typicode.com/posts",
    "https://official-joke-api.appspot.com/random_joke",
    "https://api.agify.io/?name=michael",
    "https://api.genderize.io/?name=alex"
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

                    # Smart SRE alert escalation
                    if status != 200:

                        FAIL_COUNT[url] = FAIL_COUNT.get(url, 0) + 1

                        if FAIL_COUNT[url] >= 3:
                            send_alert(url, status)
                            FAIL_COUNT[url] = 0

                    else:
                        FAIL_COUNT[url] = 0

                except requests.exceptions.RequestException:

                    status = 500
                    response_time = 0
                    send_alert(url, status)

                # Risk prediction
                risk = "LOW RISK" if status == 200 else "HIGH RISK"

                # Save log to database
                cursor.execute("""
                    INSERT INTO logs(api_url,status_code,response_time,timestamp)
                    VALUES (?,?,?,CURRENT_TIMESTAMP)
                """, (url, status, response_time))

                # Save result for dashboard
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