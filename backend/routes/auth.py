import re
import secrets
import logging
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from backend.extensions import db
from backend.models import Admin, PasswordResetToken

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def is_valid_email(email):
    return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email) is not None


# ---------- US-1.1 SIGNUP ----------
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''

    # Validate required fields
    if not full_name:
        return jsonify({'error': 'Full name is required'}), 400
    if not email or not is_valid_email(email):
        return jsonify({'error': 'A valid email is required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    # Check if email already exists
    if Admin.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    # Create new admin
    new_admin = Admin(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'}), 201


# ---------- US-1.2 LOGIN ----------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    remember = data.get('remember', False)

    if not email or not password:
        return jsonify({'error': 'Invalid email or password'}), 401

    admin = Admin.query.filter_by(email=email).first()

    # Generic error — never reveal which field is wrong
    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Set session lifetime based on Remember Me
    session.permanent = bool(remember)

    login_user(admin, remember=bool(remember))

    return jsonify({
        'message': 'Login successful',
        'admin': {
            'id': admin.id,
            'full_name': admin.full_name,
            'email': admin.email
        }
    }), 200


# ---------- LOGOUT ----------
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


# ---------- GET CURRENT USER (session restore) ----------
@auth_bp.route('/me', methods=['GET'])
def me():
    if current_user.is_authenticated:
        return jsonify({
            'id': current_user.id,
            'full_name': current_user.full_name,
            'email': current_user.email
        }), 200
    return jsonify({'error': 'Not authenticated'}), 401


# ---------- US-1.3 FORGOT PASSWORD ----------
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()

    # Always return success regardless of whether email exists (privacy)
    if email and is_valid_email(email):
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            # Generate a secure token
            token = secrets.token_hex(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)

            reset_token = PasswordResetToken(
                admin_id=admin.id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(reset_token)
            db.session.commit()

            # Log the reset link internally (no email sending needed)
            reset_link = f"http://localhost:5000/reset-password/{token}"
            current_app.logger.warning(f"[RESET LINK] Email: {email} | Link: {reset_link}")

            # Write to log file for easy access
            import os
            log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'reset_links.log')
            with open(log_path, 'a') as f:
                f.write(f"\n[{datetime.utcnow()}] Email: {email}\nLink: {reset_link}\n")

    return jsonify({'message': 'If that email is registered, a reset link has been sent'}), 200


# ---------- VALIDATE RESET TOKEN ----------
@auth_bp.route('/reset-password/<token>', methods=['GET'])
def validate_reset_token(token):
    reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()

    if not reset_token or reset_token.expires_at < datetime.utcnow():
        return jsonify({'error': 'This reset link is invalid or has expired'}), 400

    return jsonify({'message': 'Token is valid'}), 200
