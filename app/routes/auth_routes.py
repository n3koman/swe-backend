from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Use the Role.BUYER enum instead of the string 'buyer'
    new_user = User(name=name, email=email, password=password, phone_number=phone_number, role=Role.BUYER)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
