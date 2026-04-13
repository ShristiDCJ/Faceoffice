from flask import Flask
from flask_mail import Mail
from config import config
from app.models import db
import os

mail = Mail()

def create_app(config_name=None):
    """Flask app factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Set up static folder path
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')

    app = Flask(__name__, static_folder=static_path, static_url_path='/static')
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)

    # Register error handlers
    register_error_handlers(app)

    # Create app context for DB operations
    with app.app_context():
        db.create_all()

        # Start APScheduler for reminders
        from app.services.notification import start_scheduler
        start_scheduler()

    # Register blueprints
    from app.routes import visitor_bp, auth_bp, employee_bp, admin_bp
    app.register_blueprint(visitor_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(admin_bp)

    # Root route redirect
    @app.route('/')
    def index():
        from flask import redirect
        return redirect('/visitor')

    return app

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {'error': 'Internal server error'}, 500
