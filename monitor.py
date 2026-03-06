from alert import send_alert
import requests
import sqlite3
import time

DB = "data/api_logs.db"

API_LIST = [
    "https://jsonplaceholder.typicode.com/posts",
    "https://jsonplaceholder.typicode.com/users",
    "https://invalid-api-test.com"
]

def monitor_api():

    results = []

    for url in API_LIST:

        start = time.time()

        try:
            response = requests.get(url, timeout=5)

            status = response.status_code
            if status != 200:
                send_alert(url, status)
            
            response_time = round(time.time() - start,3)

        except requests.exceptions.RequestException:

            status = 500
            response_time = 0

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO logs(api_url,status_code,response_time) VALUES (?,?,?)",
            (url,status,response_time)
        )

        conn.commit()
        conn.close()

        results.append((url,status,response_time))

    return results