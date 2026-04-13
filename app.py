from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
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


# ---------------- MONITOR ----------------
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
            "INSERT INTO logs (api_url, status_code, response_time) VALUES (?, ?, ?)",
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
            flash("Login successful!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")


# ✅ FIXED SIGNUP (ONLY ONE FUNCTION)
@app.route("/signup", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("All fields are required!", "danger")
            return redirect("/signup")

        if len(password) < 4:
            flash("Password must be at least 4 characters!", "warning")
            return redirect("/signup")

        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        existing = cursor.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if existing:
            conn.close()
            flash("User already exists!", "warning")
            return redirect("/signup")

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

        conn.commit()
        conn.close()

        flash("Signup successful! Please login.", "success")
        return redirect("/login")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect("/login")


# ---------------- DASHBOARD ----------------
@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
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
@login_required
def add_api():
    url = request.form["api_url"]

    conn = get_db()
    cursor = conn.cursor()

    existing = cursor.execute("SELECT * FROM apis WHERE url=?", (url,)).fetchone()

    if existing:
        conn.close()
        flash("API already exists!", "warning")
        return redirect("/dashboard")

    cursor.execute("INSERT INTO apis (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()

    flash("API added successfully!", "success")
    return redirect("/dashboard")


# ---------------- DELETE API ----------------
@app.route("/delete-api/<int:id>", methods=["POST"])
@login_required
def delete_api(id):
    conn = get_db()

    conn.execute("DELETE FROM apis WHERE id=?", (id,))
    conn.execute("DELETE FROM logs WHERE api_url NOT IN (SELECT url FROM apis)")

    conn.commit()
    conn.close()

    flash("API deleted!", "info")
    return redirect("/dashboard")


# ---------------- CLEAR LOGS ----------------
@app.route("/clear-logs", methods=["POST"])
@login_required
def clear_logs():
    conn = get_db()
    conn.execute("DELETE FROM logs")
    conn.commit()
    conn.close()

    flash("Logs cleared!", "warning")
    return redirect("/dashboard")


# ---------------- STATS ----------------
@app.route("/api/stats")
@login_required
def stats():
    conn = get_db()

    rows = conn.execute("SELECT api_url, status_code FROM logs").fetchall()

    total_logs = len(rows)
    success_logs = sum(1 for r in rows if r["status_code"] == 200)

    uptime = (success_logs / total_logs * 100) if total_logs > 0 else 0

    latest = conn.execute("""
        SELECT api_url, status_code
        FROM logs
        WHERE id IN (
            SELECT MAX(id) FROM logs GROUP BY api_url
        )
    """).fetchall()

    total = len(latest)
    healthy = sum(1 for r in latest if r["status_code"] == 200)
    failed = total - healthy

    avg = conn.execute("SELECT AVG(response_time) as avg FROM logs").fetchone()["avg"] or 0

    conn.close()

    return jsonify({
        "total": total,
        "healthy": healthy,
        "failed": failed,
        "avg_time": round(avg, 3),
        "uptime": round(uptime, 2)
    })


# ---------------- GRAPH ----------------
@app.route("/api/response-times")
@login_required
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
@login_required
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


# ---------------- UPTIME PER API ----------------
@app.route("/api/uptime-per-api")
@login_required
def uptime_per_api():
    conn = get_db()

    rows = conn.execute("""
        SELECT api_url,
               COUNT(*) as total,
               SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as success
        FROM logs
        GROUP BY api_url
    """).fetchall()

    result = []

    for r in rows:
        total = r["total"]
        success = r["success"] or 0
        uptime = (success / total * 100) if total > 0 else 0

        result.append({
            "api": r["api_url"],
            "uptime": round(uptime, 2)
        })

    conn.close()

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)