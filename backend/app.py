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

    # Return JSON 401 for API routes instead of HTML redirect
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify
        return jsonify({'error': 'Not authenticated. Please log in.'}), 401

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(user_id)

    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.opportunities import opp_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(opp_bp)

    # Serve the frontend UI
    @app.route('/')
    def index():
        return send_from_directory('../sky', 'admin.html')

    # Handle reset password links
    @app.route('/reset-password/<token>')
    def reset_password_page(token):
        from backend.models import PasswordResetToken
        from datetime import datetime
        reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()

        if not reset_token or reset_token.expires_at < datetime.utcnow():
            return '''
                <html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#fff5f5">
                <h2 style="color:#c0392b">⛔ Link Expired or Invalid</h2>
                <p>This password reset link has expired or has already been used.</p>
                <p>Reset links are only valid for <strong>1 hour</strong>.</p>
                <a href="/" style="color:#2980b9">← Back to Login</a>
                </body></html>
            ''', 400

        return '''
            <html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#f0fff4">
            <h2 style="color:#27ae60">✅ Reset Link is Valid</h2>
            <p>This link is valid. In a full implementation, a password reset form would appear here.</p>
            <p style="color:#888;font-size:13px">This link will expire 1 hour from when it was generated.</p>
            <a href="/" style="color:#2980b9">← Back to Login</a>
            </body></html>
        ''', 200

    # Add a debug route to check auth status
    @app.route('/api/debug/whoami')
    def whoami():
        from flask_login import current_user
        from flask import jsonify
        if current_user.is_authenticated:
            return jsonify({'logged_in': True, 'admin_id': current_user.id, 'email': current_user.email})
        return jsonify({'logged_in': False}), 401

    # Create database tables on first run
    with app.app_context():
        db.create_all()

    return app
