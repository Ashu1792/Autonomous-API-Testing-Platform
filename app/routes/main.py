from flask import Flask, session, redirect
from functools import wraps
import threading
import time
<<<<<<< HEAD
from app.services.monitor import monitor_apis
=======
from app.services.monitor import monitor_api

>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper


def background_monitor():
    while True:
<<<<<<< HEAD
        monitor_apis()
=======
        monitor_api()
>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
        time.sleep(10)


def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    threading.Thread(target=background_monitor, daemon=True).start()

    return app