from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS  # Import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    # Enable CORS for all routes
    CORS(app)  # This allows requests from any origin. For specific origins: CORS(app, resources={r"/*": {"origins": "https://your-frontend-url.com"}})

    # Register your blueprints (auth routes)
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    return app
