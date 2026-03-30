from models.train_model import train_model
from scheduler import start_scheduler
import sqlite3
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from monitor import monitor_api
from contract_test import validate_contract

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------------- LOGIN MANAGER ----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- DATABASES ----------------

# 👉 USERS DATABASE
def get_user_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# 👉 API LOGS DATABASE
def get_api_db():
    conn = sqlite3.connect("data/api_logs.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- CREATE USERS TABLE ----------------
def create_users_table():
    conn = get_user_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.close()

create_users_table()

# ---------------- USER CLASS ----------------
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_user_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()

    if user:
        return User(user["id"], user["username"], user["role"])
    return None

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        confirm = request.form.get("confirmPassword")

        if not username or not password:
            flash("All fields are required!")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match!")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_user_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists!")
        finally:
            conn.close()

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_user_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            login_user(User(user["id"], user["username"], user["role"]))
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/")
@login_required
def dashboard():

    # ✅ ML MODEL
    model, accuracy = train_model()
    accuracy = round(accuracy * 100, 2) if accuracy else 0

    # ✅ MONITORING
    results = monitor_api()
    contract = validate_contract()

    labels, times = get_logs()
    failures = get_failures()

    total = len(results)
    healthy = len([r for r in results if r["status"] == 200])
    failed = total - healthy

    avg_time = round(sum(r["response_time"] for r in results) / total, 3) if total > 0 else 0
    risk_score = calculate_risk_score(results)

    return render_template(
        "dashboard.html",
        user=current_user.username,
        role=current_user.role,
        results=results,
        labels=labels,
        times=times,
        failures=failures,
        total=total,
        healthy=healthy,
        failed=failed,
        avg_time=avg_time,
        risk_score=risk_score,
        accuracy=accuracy   # ✅ VERY IMPORTANT
    )

# ---------------- ADMIN ONLY DELETE ----------------
@app.route("/delete-api/<int:id>")
@login_required
def delete_api(id):

    if current_user.role != "admin":
        return "❌ Access Denied (Admin only)"

    conn = get_api_db()
    conn.execute("DELETE FROM logs WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------- API CHART DATA ----------------
@app.route("/api/chart-data")
@login_required
def chart_data():

    labels, times = get_logs()

    return jsonify({
        "labels": labels,
        "times": times
    })

# ---------------- LOG FUNCTIONS ----------------
def get_logs():

    conn = get_api_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT response_time, timestamp
        FROM logs
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    rows.reverse()

    labels = []
    times = []

    for r in rows:
        times.append(r[0])
        labels.append(r[1][-8:])

    return labels, times


def get_failures():

    conn = get_api_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT api_url, status_code, timestamp
        FROM logs
        WHERE status_code != 200
        ORDER BY id DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows

# ---------------- RISK SCORE ----------------
def calculate_risk_score(results):

    score = 0

    for r in results:

        if r["status"] != 200:
            score += 40
        elif r["response_time"] > 1:
            score += 20
        elif r["response_time"] > 0.5:
            score += 10

    return min(score, 100)

# ---------------- RUN ----------------
if __name__ == "__main__":

    start_scheduler()
    app.run(debug=True)