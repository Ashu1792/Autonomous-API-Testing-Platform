import sqlite3
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from monitor import monitor_api
import validators

app = Flask(__name__)
app.secret_key = "secret"

# ---------------- LOGIN ----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect("data/api_logs.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS apis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_url TEXT,
        status_code INTEGER,
        response_time REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- USER ----------------
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()

    if user:
        return User(user["id"], user["username"], user["role"] if "role" in user.keys() else "user")
    return None

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            login_user(User(user["id"], user["username"], user["role"] if "role" in user.keys() else "user"))
            return redirect("/dashboard")
        else:
            flash("Invalid credentials")

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            flash("User already exists")
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    results = monitor_api()

    total = len(results)
    healthy = len([r for r in results if r["status"] == 200])
    failed = total - healthy

    avg_time = round(sum(r["response_time"] for r in results) / total, 3) if total else 0
    risk_score = int((failed / total) * 100) if total else 0

    return render_template(
        "dashboard.html",
        user=current_user.username,
        role=current_user.role,
        results=results,
        total=total,
        healthy=healthy,
        failed=failed,
        avg_time=avg_time,
        risk_score=risk_score
    )

from flask import request, redirect, flash
import validators

@app.route("/add-api", methods=["POST"])
@login_required
def add_api():
    url = request.form.get("api_url")

    #-------- VALIDATION-----------
    if not url:
        flash("URL is required")
        return redirect("/dashboard")

    if not url.startswith("http"):
        flash("Invalid URL format (must start with http/https)")
        return redirect("/dashboard")

    if len(url) > 255:
        flash("URL too long")
        return redirect("/dashboard")

    if not validators.url(url):
        flash("Invalid URL")
        return redirect("/dashboard")

    conn = get_db()
    try:
        conn.execute("INSERT INTO apis (url) VALUES (?)", (url,))
        conn.commit()
        flash("API added successfully")
    except Exception as e:
        flash("API already exists or database error")
    finally:
        conn.close()

    return redirect("/dashboard")

#---------------- DELETE API ----------------

@app.route("/delete-api/<int:id>", methods=["POST"])
@login_required
def delete_api(id):
    if current_user.role != "admin":
        flash("Not authorized")
        return redirect("/dashboard")

    conn = get_db()

    api = conn.execute("SELECT url FROM apis WHERE id=?", (id,)).fetchone()

    if api:
        conn.execute("DELETE FROM logs WHERE api_url=?", (api["url"],))

    conn.execute("DELETE FROM apis WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
#-----------api stats----------------
@app.route("/api/stats")
def stats():
    conn = get_db()

    # only logs of current APIs
    rows = conn.execute("""
        SELECT status_code FROM logs
        WHERE api_url IN (SELECT url FROM apis)
        ORDER BY id DESC LIMIT 20
    """).fetchall()

    healthy = sum(1 for r in rows if r["status_code"] == 200)
    failed = sum(1 for r in rows if r["status_code"] != 200)

    total = conn.execute("SELECT COUNT(*) FROM apis").fetchone()[0]

    avg = conn.execute("""
        SELECT AVG(response_time) FROM logs
        WHERE api_url IN (SELECT url FROM apis)
    """).fetchone()[0] or 0

    conn.close()

    return jsonify({
        "total": total,
        "healthy": healthy,
        "failed": failed,
        "avg_time": round(avg, 3)
    })
@app.route("/api/response-times")
def response_times():
    conn = get_db()

    rows = conn.execute("""
        SELECT timestamp, response_time FROM logs
        WHERE api_url IN (SELECT url FROM apis)
        ORDER BY id DESC LIMIT 10
    """).fetchall()

    conn.close()

    return jsonify({
        "labels": [r["timestamp"][-8:] for r in rows][::-1],
        "values": [r["response_time"] for r in rows][::-1]
    })

@app.route("/api/failures")
def failures():
    conn = get_db()

    rows = conn.execute("""
        SELECT api_url, timestamp FROM logs
        WHERE status_code != 200
        AND api_url IN (SELECT url FROM apis)
        ORDER BY id DESC LIMIT 10
    """).fetchall()

    conn.close()

    return jsonify([{"url": r["api_url"], "time": r["timestamp"]} for r in rows])

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)