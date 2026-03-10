from alert import send_alert
import requests
import sqlite3
import time

DB = "data/api_logs.db"

API_LIST = [
    "https://api.openweathermap.org/data/2.5/weather?q=London&appid=b452d4b9373592eb07f553041a7e5038",
    "https://jsonplaceholder.typicode.com/posts",
    "https://api.github.com/users/octocat"
    "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
]


def monitor_api():

    results = []

    # open database connection once
    conn = sqlite3.connect(DB)
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

        # simple failure prediction
        if status == 200:
            risk = "LOW RISK"
        else:
            risk = "HIGH RISK"

        # save logs
        cursor.execute(
            "INSERT INTO logs(api_url,status_code,response_time) VALUES (?,?,?)",
            (url, status, response_time)
        )

        # append dictionary (better for dashboard)
        results.append({
            "api": url,
            "status": status,
            "response_time": response_time,
            "risk": risk
        })

    conn.commit()
    conn.close()

    return results