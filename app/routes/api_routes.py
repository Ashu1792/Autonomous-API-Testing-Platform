from flask import Blueprint, request, redirect
from app.models.database import get_db
from app.routes.main import login_required
import requests
import time

# ✅ ONLY ONE BLUEPRINT
api_bp = Blueprint("api", __name__)

@api_bp.route("/add_api", methods=["POST"])
@login_required
def add_api():
    print("🔥 ADD API HIT")

    url = request.form.get("url")
    print("URL:", url)

    if not url:
        return redirect("/dashboard")

    conn = get_db()
    cursor = conn.cursor()

    # insert api (avoid duplicates)
    cursor.execute("INSERT OR IGNORE INTO apis (url) VALUES (?)", (url,))

    # 🔥 check api instantly
    start = time.time()
    try:
        res = requests.get(url, timeout=5)
        status = res.status_code
    except:
        status = 500

    response_time = round(time.time() - start, 3)

    # insert log
    cursor.execute("""
        INSERT INTO logs (api_url, status_code, response_time)
        VALUES (?, ?, ?)
    """, (url, status, response_time))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@api_bp.route("/delete/<int:id>")
@login_required
def delete_api(id):
    conn = get_db()

    api = conn.execute(
        "SELECT url FROM apis WHERE id=?",
        (id,)
    ).fetchone()

    if api:
        conn.execute("DELETE FROM apis WHERE id=?", (id,))
        conn.execute("DELETE FROM logs WHERE api_url=?", (api["url"],))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@api_bp.route("/clear_history")
@login_required
def clear_history():
    conn = get_db()
    conn.execute("DELETE FROM logs")
    conn.commit()
    conn.close()

    return redirect("/dashboard")