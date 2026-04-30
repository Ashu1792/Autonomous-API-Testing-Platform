import os
from flask import Flask

def create_app():
    # Absolute project root path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    template_dir = os.path.join(project_root, "templates")
    static_dir = os.path.join(project_root, "static")
    
    print("PROJECT ROOT:", project_root)
    print("TEMPLATE DIR:", template_dir)

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    print("Flask template folder:", app.template_folder)

    app.secret_key = "supersecretkey"

    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    return app