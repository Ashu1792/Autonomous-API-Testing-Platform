from apscheduler.schedulers.background import BackgroundScheduler
from monitor import monitor_api

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            monitor_api,
            "interval",
            seconds=10,
            id="api_monitor_job",          # ✅ unique ID
            max_instances=1,               # ✅ prevent overlap
            coalesce=True,                # ✅ merge skipped runs
            replace_existing=True         # ✅ avoid duplicates
        )

        scheduler.start()
        print("✅ API Monitoring Scheduler Started...")