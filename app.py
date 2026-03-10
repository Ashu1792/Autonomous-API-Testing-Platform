from scheduler import start_scheduler
import sqlite3
from flask import Flask, render_template
from monitor import monitor_api
from contract_test import validate_contract

app = Flask(__name__)


@app.route("/")
def dashboard():

    results = monitor_api()

    contract = validate_contract()

    labels, times = get_logs()

    total = len(results)

    healthy = len([r for r in results if r["status"] == 200])

    failed = total - healthy

    avg_time = round(sum(r["response_time"] for r in results)/total,3) if total > 0 else 0

    return render_template(
        "dashboard.html",
        results=results,
        contract=contract,
        labels=labels,
        times=times,
        total=total,
        healthy=healthy,
        failed=failed,
        avg_time=avg_time
    )

def get_logs():

    conn = sqlite3.connect("data/api_logs.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT response_time, timestamp FROM logs ORDER BY id DESC LIMIT 10"
    )

    rows = cursor.fetchall()

    conn.close()

    rows.reverse()

    times = [row[0] for row in rows]
    labels = [row[1] for row in rows]

    return labels, times


if __name__ == "__main__":

    # start background scheduler
    start_scheduler()

    app.run(debug=True)