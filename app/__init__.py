from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO  # Add Socket.IO import
from config import Config


# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")  # Initialize Socket.IO


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    jwt.init_app(app)
    CORS(app)
    socketio.init_app(app)  # Initialize Socket.IO with app

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.farmer_routes import farmer_bp
    from app.routes.buyer_routes import buyer_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(farmer_bp, url_prefix="/farmer")
    app.register_blueprint(buyer_bp, url_prefix="/buyer")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.socket_events import register_socket_events

    register_socket_events(socketio)  # Custom function to handle Socket.IO events
    return app
