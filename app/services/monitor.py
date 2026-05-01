import time
import requests
from app.models.database import get_db
from app.services.email_service import send_email_alert

# 🔥 Track last status to avoid spam
last_status = {}

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
                is_up = 200 <= status < 400
            except:
                status = 500
                is_up = False

            response_time = round(time.time() - start, 3)

            # 🔹 Save logs
            conn.execute("""
                INSERT INTO logs (api_url, status_code, response_time)
                VALUES (?, ?, ?)
            """, (url, status, response_time))

            # 🔥 EMAIL ALERT LOGIC
            prev_status = last_status.get(url, True)

            if prev_status != is_up:
                if not is_up:
                    send_email_alert(
                        "🚨 API DOWN",
                        f"{url} is DOWN (status: {status})",
                        "Ashupal1507@gmail.com"
                    )
                    print(f"🚨 ALERT SENT: {url} DOWN")

                else:
                    send_email_alert(
                        "✅ API RECOVERED",
                        f"{url} is BACK UP",
                        "Ashupal1507@gmail.com"
                    )
                    print(f"✅ RECOVERY EMAIL SENT: {url}")

            # update status
            last_status[url] = is_up

        conn.commit()
        conn.close()

        print("🔄 Monitoring running...")

        # ✅ only ONE sleep needed
        time.sleep(10)