from app import create_app
from threading import Thread
from app.services.monitor import monitor_apis

app = create_app()

# 🔥 start monitoring
t = Thread(target=monitor_apis)
t.daemon = True
t.start()

if __name__ == "__main__":
    app.run(debug=True)