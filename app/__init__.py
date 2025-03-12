from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from .config import Config


# Initialize extensions (without attaching to app yet)
db = SQLAlchemy(app)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    app.register_blueprint(main)

    # Import and register blueprints/views inside the function
    from app import views  
    return app
