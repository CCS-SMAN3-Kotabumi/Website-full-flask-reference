from flask import Flask
import click

from app.extensions import csrf, db, login_manager, migrate


def create_app(config_override=None):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    if config_override:
        app.config.update(config_override)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # loder user admin untuk Flask-Login (lazy untuk menghindari circular import).
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Admin
        return Admin.query.get(int(user_id))

    # Register blueprint
    from app.routes.main import bp as main_bp
    from app.routes.registration import bp as reg_bp
    from app.routes.admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(reg_bp)
    app.register_blueprint(admin_bp)

    _register_cli(app)

    return app


def _register_cli(app):
    """CLI command untuk buat akun admin."""

    @app.cli.command('create-admin')
    @click.option('--username', required=True)
    @click.option('--password', required=True)
    def create_admin(username, password):
        """Buat akun admin (password disimpan hashed)."""
        from app.models import Admin

        if Admin.query.filter_by(username=username).first():
            click.echo('Admin "%s" sudah ada.' % username)
            return
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo('Admin "%s" tersimpan (password hashed).' % username)