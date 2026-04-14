from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import requests
import time
import threading
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB = "data/api_logs.db"


# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- LOGIN REQUIRED ----------------
def login_required(func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ---------------- BACKGROUND MONITOR ----------------
def monitor_api():
    conn = get_db()
    cursor = conn.cursor()

    apis = cursor.execute("SELECT * FROM apis").fetchall()

    for api in apis:
        url = api["url"]

        try:
            start = time.time()
            res = requests.get(url, timeout=5)
            response_time = round(time.time() - start, 3)
            status = res.status_code
        except:
            response_time = -1
            status = 500

        cursor.execute(
            "INSERT INTO logs (api_url, status_code, response_time, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (url, status, response_time)
        )

    conn.commit()
    conn.close()


def background_monitor():
    while True:
        monitor_api()
        time.sleep(10)


threading.Thread(target=background_monitor, daemon=True).start()


# ---------------- AUTH ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect("/dashboard")
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        cursor = conn.cursor()

        existing = cursor.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if existing:
            flash("User already exists!", "warning")
            return redirect("/signup")

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- DASHBOARD ----------------
@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()

    # ---------------- LATEST STATUS ----------------
    rows = conn.execute("""
        SELECT a.id, a.url,
               l.status_code,
               l.response_time
        FROM apis a
        LEFT JOIN logs l ON a.url = l.api_url
        WHERE l.id IN (
            SELECT MAX(id) FROM logs GROUP BY api_url
        )
    """).fetchall()

    apis = []
    for r in rows:
        status = "Healthy" if r["status_code"] == 200 else "Failed"

        apis.append({
            "id": r["id"],
            "url": r["url"],
            "status": status,
            "response_time": r["response_time"] if r["response_time"] else 0,
            "uptime": 0
        })

    # ---------------- STATS ----------------
    total = len(apis)
    healthy = sum(1 for a in apis if a["status"] == "Healthy")
    failed = total - healthy

    avg_time = conn.execute("SELECT AVG(response_time) as avg FROM logs").fetchone()["avg"] or 0

    logs = conn.execute("SELECT * FROM logs").fetchall()
    total_logs = len(logs)
    success_logs = sum(1 for l in logs if l["status_code"] == 200)
    uptime = (success_logs / total_logs * 100) if total_logs else 0

    # ---------------- CHART ----------------
    chart_rows = conn.execute("""
        SELECT response_time, timestamp
        FROM logs ORDER BY id DESC LIMIT 10
    """).fetchall()

    chart_labels = [r["timestamp"][-8:] for r in chart_rows if r["timestamp"]][::-1]
    chart_data = [r["response_time"] for r in chart_rows][::-1]

    # ---------------- FAILED LOGS (FIXED) ----------------
    failed_rows = conn.execute("""
        SELECT api_url, timestamp
        FROM logs
        WHERE status_code != 200
        ORDER BY id DESC LIMIT 5
    """).fetchall()

    failed_logs = [
        {
            "url": r["api_url"],
            "time": r["timestamp"]
        }
        for r in failed_rows
    ]

    # ---------------- UPTIME PER API ----------------
    uptime_rows = conn.execute("""
        SELECT api_url,
               COUNT(*) as total,
               SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as success
        FROM logs
        GROUP BY api_url
    """).fetchall()

    uptime_map = {}
    for r in uptime_rows:
        total_r = r["total"]
        success_r = r["success"] or 0
        uptime_map[r["api_url"]] = round((success_r / total_r * 100), 2) if total_r else 0

    for api in apis:
        api["uptime"] = uptime_map.get(api["url"], 0)

    conn.close()

    return render_template("dashboard.html",
                           total=total,
                           healthy=healthy,
                           failed=failed,
                           avg_time=round(avg_time, 3),
                           uptime=round(uptime, 2),
                           apis=apis,
                           failed_logs=failed_logs,
                           chart_labels=chart_labels,
                           chart_data=chart_data)


# ---------------- ADD API ----------------
@app.route("/add_api", methods=["POST"])
@login_required
def add_api():
    url = request.form["url"]

    conn = get_db()
    cursor = conn.cursor()

    existing = cursor.execute("SELECT * FROM apis WHERE url=?", (url,)).fetchone()

    if not existing:
        cursor.execute("INSERT INTO apis (url) VALUES (?)", (url,))
        conn.commit()

    conn.close()
    return redirect("/dashboard")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
@login_required
def delete_api(id):
    conn = get_db()

    api = conn.execute("SELECT url FROM apis WHERE id=?", (id,)).fetchone()

    if api:
        conn.execute("DELETE FROM apis WHERE id=?", (id,))
        conn.execute("DELETE FROM logs WHERE api_url=?", (api["url"],))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- CLEAR HISTORY ----------------
@app.route("/clear_history")
@login_required
def clear_history():
    conn = get_db()
    conn.execute("DELETE FROM logs")
    conn.commit()
    conn.close()

    return redirect("/dashboard")


if __name__ == "__main__":
    app.run(debug=True)