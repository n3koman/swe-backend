from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import User
from app import db

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/user/<int:user_id>/role", methods=["GET"])
@jwt_required()
def get_user_role(user_id):
    """
    Get the role (user type) of a user by their user ID.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"role": user.role.name}), 200
