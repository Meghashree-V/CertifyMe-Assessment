import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.config import Config
from backend.extensions import db, login_manager
from backend.models import Admin


def create_app():
    app = Flask(__name__, static_folder='../sky', static_url_path='')

    app.config.from_object(Config)

    CORS(app, supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # Register blueprints
    from backend.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Serve the frontend UI
    @app.route('/')
    def index():
        return send_from_directory('../sky', 'admin.html')

    # Create database tables on first run
    with app.app_context():
        db.create_all()

    return app
