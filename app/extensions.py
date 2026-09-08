from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# Endpoint untuk redirect bila user unauthenticated mengakses rute protected.
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Log in admin untuk lanjut.'