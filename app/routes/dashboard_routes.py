from flask import Blueprint, render_template
from app.models.database import get_db
from app.routes.main import login_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()

    # 🔹 latest logs per API
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

    # 🔥 UPTIME CALCULATION
    uptime_data = {}
    for api in conn.execute("SELECT url FROM apis").fetchall():
        url = api["url"]

        logs = conn.execute(
            "SELECT status_code FROM logs WHERE api_url=?",
            (url,)
        ).fetchall()

        if logs:
            total_logs = len(logs)
            success = sum(1 for log in logs if log["status_code"] == 200)
            uptime_data[url] = round((success / total_logs) * 100, 2)
        else:
            uptime_data[url] = 0

    # 🔹 API LIST
    apis = []
    for r in rows:
        status = "Healthy" if r["status_code"] == 200 else "Failed"

        apis.append({
            "id": r["id"],
            "url": r["url"],
            "status": status,
            "response_time": r["response_time"] or 0,
            "uptime": uptime_data.get(r["url"], 0)
        })

    total = len(apis)
    healthy = sum(1 for a in apis if a["status"] == "Healthy")
    failed = total - healthy

    # 🔹 AVG TIME
    avg_row = conn.execute("SELECT AVG(response_time) as avg FROM logs").fetchone()
    avg_time = avg_row["avg"] or 0

    # 🔹 FAILED LOGS
    failed_logs = conn.execute("""
        SELECT api_url as url, timestamp as time
        FROM logs
        WHERE status_code != 200
        ORDER BY timestamp DESC
        LIMIT 5
    """).fetchall()

    # 🔹 CHART DATA
    chart_rows = conn.execute("""
        SELECT timestamp, response_time
        FROM logs
        ORDER BY timestamp ASC
        LIMIT 10
    """).fetchall()

    chart_labels = [r["timestamp"] for r in chart_rows]
    chart_data = [r["response_time"] for r in chart_rows]

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        healthy=healthy,
        failed=failed,
        avg_time=round(avg_time, 3),
        uptime=round((healthy / total) * 100, 2) if total > 0 else 0,
        apis=apis,
        failed_logs=failed_logs,
        chart_labels=chart_labels,
        chart_data=chart_data
    )