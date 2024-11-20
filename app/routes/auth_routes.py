from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Farmer, Buyer, Role
from twilio.rest import Client  # or any email/SMS provider library for sending verification
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint('auth', __name__)

# Get the secret key from the environment variable
SECRET_KEY = os.getenv('SECRET_KEY')

# Farmer Registration Endpoint
import traceback  # Import to help with logging stack traces

@auth_bp.route('/register/farmer', methods=['POST'])
def register_farmer():
    try:
        data = request.get_json()

        required_fields = ['name', 'email', 'password', 'phone_number', 'farm_address', 'farm_size', 'crops', 'gov_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        name = data['name']
        email = data['email']
        password = data['password']
        phone_number = data['phone_number']
        farm_address = data['farm_address']
        farm_size = data['farm_size']
        crops = data['crops']
        gov_id = data['gov_id']


        if User.query.filter((User.email == email) | (User.phone_number == phone_number)).first():
            return jsonify({"error": "Email or phone number is already in use"}), 409

        hashed_password = generate_password_hash(password)

        new_farmer = Farmer(
            name=name,
            email=email,
            phone_number=phone_number,
            password=hashed_password,
            role=Role.FARMER,
            farm_address=farm_address,
            farm_size=farm_size,
            crop_types=crops,
            gov_id=gov_id
        )

        db.session.add(new_farmer)
        db.session.commit()

        return jsonify({"message": "Farmer registered successfully."}), 201

    except Exception as e:
        db.session.rollback()
        print("Exception occurred:", e)
        traceback.print_exc()  # This prints the full stack trace
        return jsonify({"error": str(e)}), 500

# Buyer Registration Endpoint
@auth_bp.route('/register/buyer', methods=['POST'])
def register_buyer():
    data = request.get_json()

    required_fields = ['name', 'email', 'phone_number', 'delivery_address', 'password']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    name = data['name']
    email = data['email']
    phone_number = data['phone_number']
    delivery_address = data['delivery_address']
    password = data['password']

    if User.query.filter((User.email == email) | (User.phone_number == phone_number)).first():
        return jsonify({"error": "Email or phone number is already in use"}), 409

    hashed_password = generate_password_hash(password)

    new_buyer = Buyer(
        name=name,
        email=email,
        phone_number=phone_number,
        password=hashed_password,
        role=Role.BUYER,
        delivery_address=delivery_address
    )

    try:
        db.session.add(new_buyer)
        db.session.commit()
        return jsonify({"message": "Buyer registered successfully."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        token = jwt.encode({
            'user_id': user.id,
            'sub': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401