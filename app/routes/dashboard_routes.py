from flask import Blueprint, render_template
from app.models.database import get_db
from app.routes.main import login_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()

<<<<<<< HEAD
    # 🔹 latest logs per API
=======
<<<<<<< HEAD
    # 🔹 latest logs per API
=======
<<<<<<< HEAD
    # 🔹 latest logs per API
=======
>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
>>>>>>> 2789ad30ad4dd1b7f064c94d07fffe2586c764e6
>>>>>>> c9d2a5cf1f266020c8323cf9667461c245f650fd
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

<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 2789ad30ad4dd1b7f064c94d07fffe2586c764e6
>>>>>>> c9d2a5cf1f266020c8323cf9667461c245f650fd
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
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
=======
>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
>>>>>>> 2789ad30ad4dd1b7f064c94d07fffe2586c764e6
>>>>>>> c9d2a5cf1f266020c8323cf9667461c245f650fd
    apis = []
    for r in rows:
        status = "Healthy" if r["status_code"] == 200 else "Failed"

        apis.append({
            "id": r["id"],
            "url": r["url"],
            "status": status,
            "response_time": r["response_time"] or 0,
<<<<<<< HEAD
            "uptime": uptime_data.get(r["url"], 0)
=======
<<<<<<< HEAD
            "uptime": uptime_data.get(r["url"], 0)
=======
<<<<<<< HEAD
            "uptime": uptime_data.get(r["url"], 0)
=======
            "uptime": 0
>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
>>>>>>> 2789ad30ad4dd1b7f064c94d07fffe2586c764e6
>>>>>>> c9d2a5cf1f266020c8323cf9667461c245f650fd
        })

    total = len(apis)
    healthy = sum(1 for a in apis if a["status"] == "Healthy")
    failed = total - healthy

<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 2789ad30ad4dd1b7f064c94d07fffe2586c764e6
>>>>>>> c9d2a5cf1f266020c8323cf9667461c245f650fd
    # 🔹 AVG TIME
    avg_row = conn.execute("SELECT AVG(response_time) as avg FROM logs").fetchone()
    avg_time = avg_row["avg"] or 0

    # 🔹 FAILED LOGS
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
=======
    # ✅ FIX 1: UPTIME
    if total > 0:
        uptime = (healthy / total) * 100
    else:
        uptime = 0

    # ✅ FIX 2: AVG TIME
    avg_row = conn.execute("SELECT AVG(response_time) as avg FROM logs").fetchone()
    avg_time = avg_row["avg"] or 0

    # ✅ FIX 3: FAILED LOGS
>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
>>>>>>> 2789ad30ad4dd1b7f064c94d07fffe2586c764e6
>>>>>>> c9d2a5cf1f266020c8323cf9667461c245f650fd
    failed_logs = conn.execute("""
        SELECT api_url as url, timestamp as time
        FROM logs
        WHERE status_code != 200
        ORDER BY timestamp DESC
        LIMIT 5
    """).fetchall()

<<<<<<< HEAD
    # 🔹 CHART DATA
=======
<<<<<<< HEAD
    # 🔹 CHART DATA
=======
<<<<<<< HEAD
    # 🔹 CHART DATA
=======
    # ✅ FIX 4: CHART DATA
>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
>>>>>>> 2789ad30ad4dd1b7f064c94d07fffe2586c764e6
>>>>>>> c9d2a5cf1f266020c8323cf9667461c245f650fd
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
<<<<<<< HEAD
        uptime=round((healthy / total) * 100, 2) if total > 0 else 0,
=======
<<<<<<< HEAD
        uptime=round((healthy / total) * 100, 2) if total > 0 else 0,
=======
<<<<<<< HEAD
        uptime=round((healthy / total) * 100, 2) if total > 0 else 0,
=======
        uptime=round(uptime, 2),
>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
>>>>>>> 2789ad30ad4dd1b7f064c94d07fffe2586c764e6
>>>>>>> c9d2a5cf1f266020c8323cf9667461c245f650fd
        apis=apis,
        failed_logs=failed_logs,
        chart_labels=chart_labels,
        chart_data=chart_data
    )