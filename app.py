from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import requests
import time

app = Flask(__name__)

DB = "data/api_logs.db"

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- MONITOR ----------------
def monitor_api():
    conn = get_db()
    cursor = conn.cursor()

    apis = cursor.execute("SELECT * FROM apis").fetchall()

    for api in apis:
        url = api["url"]

        try:
            start = time.time()
            res = requests.get(
                url,
                timeout=5,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response_time = round(time.time() - start, 3)
            status = res.status_code
        except:
            response_time = -1
            status = 500

        cursor.execute(
            "INSERT INTO logs (api_url, status_code, response_time) VALUES (?, ?, ?)",
            (url, status, response_time)
        )

    conn.commit()
    conn.close()


# ---------------- DASHBOARD ----------------
@app.route("/")
@app.route("/dashboard")
def dashboard():

    monitor_api()

    conn = get_db()

    rows = conn.execute("""
        SELECT a.id, a.url as api_url, l.status_code, l.response_time
        FROM apis a
        LEFT JOIN logs l ON a.url = l.api_url
        WHERE l.id IN (
            SELECT MAX(id) FROM logs GROUP BY api_url
        )
    """).fetchall()

    results = [
        {
            "id": r["id"],
            "api": r["api_url"],
            "status": r["status_code"],
            "response_time": r["response_time"]
        }
        for r in rows
    ]

    conn.close()

    return render_template("dashboard.html", results=results)


# ---------------- ADD API ----------------
@app.route("/add-api", methods=["POST"])
def add_api():
    url = request.form["api_url"]

    conn = get_db()
    conn.execute("INSERT INTO apis (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# ---------------- DELETE API ----------------
@app.route("/delete-api/<int:id>", methods=["POST"])
def delete_api(id):

    conn = get_db()

    conn.execute("DELETE FROM apis WHERE id=?", (id,))
    conn.execute("DELETE FROM logs WHERE api_url NOT IN (SELECT url FROM apis)")

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# ---------------- CLEAR LOGS ----------------
@app.route("/clear-logs", methods=["POST"])
def clear_logs():
    conn = get_db()
    conn.execute("DELETE FROM logs")
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


# ---------------- STATS ----------------
@app.route("/api/stats")
def stats():
    conn = get_db()

    rows = conn.execute("""
        SELECT api_url, status_code
        FROM logs
        WHERE id IN (
            SELECT MAX(id) FROM logs GROUP BY api_url
        )
    """).fetchall()

    total = len(rows)
    healthy = sum(1 for r in rows if r["status_code"] == 200)
    failed = total - healthy

    avg = conn.execute("SELECT AVG(response_time) as avg FROM logs").fetchone()["avg"] or 0

    conn.close()

    return jsonify({
        "total": total,
        "healthy": healthy,
        "failed": failed,
        "avg_time": round(avg, 3)
    })


# ---------------- GRAPH ----------------
@app.route("/api/response-times")
def graph():
    conn = get_db()

    rows = conn.execute("""
        SELECT response_time, timestamp
        FROM logs
        ORDER BY id DESC LIMIT 10
    """).fetchall()

    labels = [r["timestamp"][-8:] for r in rows][::-1]
    values = [r["response_time"] for r in rows][::-1]

    conn.close()

    return jsonify({"labels": labels, "values": values})


# ---------------- FAILURES ----------------
@app.route("/api/failures")
def failures():
    conn = get_db()

    rows = conn.execute("""
        SELECT api_url, timestamp
        FROM logs
        WHERE status_code != 200
        ORDER BY id DESC LIMIT 5
    """).fetchall()

    conn.close()

    return jsonify([
        {"url": r["api_url"], "time": r["timestamp"]}
        for r in rows
    ])


if __name__ == "__main__":
    app.run(debug=True)