from scheduler import start_scheduler
import sqlite3
from flask import Flask, render_template, jsonify
from monitor import monitor_api
from contract_test import validate_contract

app = Flask(__name__)


@app.route("/")
def dashboard():

    results = monitor_api()
    contract = validate_contract()

    labels, times = get_logs()
    failures = get_failures()

    total = len(results)
    healthy = len([r for r in results if r["status"] == 200])
    failed = total - healthy

    avg_time = round(sum(r["response_time"] for r in results)/total,3) if total>0 else 0

    return render_template(
        "dashboard.html",
        results=results,
        labels=labels,
        times=times,
        failures=failures,
        total=total,
        healthy=healthy,
        failed=failed,
        avg_time=avg_time
    )


@app.route("/api/chart-data")
def chart_data():

    labels, times = get_logs()

    return jsonify({
        "labels": labels,
        "times": times
    })


def get_logs():

    conn = sqlite3.connect("data/api_logs.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT response_time,timestamp
        FROM logs
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    rows.reverse()

    labels=[]
    times=[]

    for r in rows:
        times.append(r[0])
        labels.append(r[1][-8:])

    return labels,times


def get_failures():

    conn = sqlite3.connect("data/api_logs.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT api_url,status_code,timestamp
    FROM logs
    WHERE status_code!=200
    ORDER BY id DESC
    LIMIT 5
    """)

    rows=cursor.fetchall()
    conn.close()

    return rows




if __name__ == "__main__":

    start_scheduler()
    app.run(debug=True)