import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'qf-admin-dev-key-2025')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///admin.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session stays alive for 30 days if Remember Me is checked
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
