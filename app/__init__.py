from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks import send_alerts

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    # Import the models after initializing db to avoid circular imports
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize APScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=send_alerts, trigger="interval", hours=24)  # Run every 24 hours
    scheduler.start()

    return app