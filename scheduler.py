from apscheduler.schedulers.background import BackgroundScheduler
from monitor import monitor_api

scheduler = BackgroundScheduler()

def start_scheduler():

    scheduler.add_job(
        func=monitor_api,
        trigger="interval",
        seconds=10
    )

    scheduler.start()

    print("API Monitoring Scheduler Started...")