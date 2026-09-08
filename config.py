import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


class Config:
    """Konfigurasi aplikasi Flask."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    # sqlite:///ccs.db otomatis disimpan di direktori instance/
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ccs.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False