from scheduler import start_scheduler
import sqlite3
from flask import Flask, render_template
from monitor import monitor_api
from contract_test import validate_contract

app = Flask(__name__)


@app.route("/")
def dashboard():

    # get API monitoring results
    results = monitor_api()

    # validate contract
    contract = validate_contract()

    # get logs for charts
    labels, times = get_logs()

    return render_template(
        "dashboard.html",
        results=results,
        contract=contract,
        labels=labels,
        times=times
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