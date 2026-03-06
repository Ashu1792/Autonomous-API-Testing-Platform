from scheduler import start_scheduler
import sqlite3
from flask import Flask,render_template
from monitor import monitor_api
from contract_test import validate_contract
from predictor import predict_risk
from scheduler import scheduler

app = Flask(__name__)

@app.route("/")
def dashboard():

    data = monitor_api()

    contract = validate_contract()

    labels,times = get_logs()

    api_data = []

    for url,status,time in data:

       risk = predict_risk(time, status)

    api_data.append({
            "url":url,
            "status":status,
            "time":time,
            "risk":risk
        })

    return render_template(
        "dashboard.html",
        apis=api_data,
        contract=contract,
        labels=labels,
        times=times
    )
def get_logs():

    conn = sqlite3.connect("data/api_logs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT response_time,timestamp FROM logs ORDER BY id DESC LIMIT 10")

    rows = cursor.fetchall()

    conn.close()

    rows.reverse()

    times = [row[0] for row in rows]
    labels = [row[1] for row in rows]

    return labels,times

if __name__ == "__main__":

    start_scheduler()

    app.run(debug=True)