from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from .config import Config

# Initialize extensions (without attaching to app yet)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Initialize Flask-Migrate
    migrate.init_app(app, db)

    # Import blueprints inside the function to avoid circular imports
    from app.views import main  # Ensure this is correctly defined
    app.register_blueprint(main)

    return app
