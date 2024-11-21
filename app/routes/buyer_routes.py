from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Buyer, Order, db
from sqlalchemy.exc import IntegrityError
import re

buyer_bp = Blueprint('buyer', __name__)

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_phone_number(phone_number):
    """Validate phone number format"""
    phone_regex = r'^\+?1?\d{10,14}$'
    return re.match(phone_regex, phone_number) is not None

@buyer_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Retrieve the profile of the logged-in buyer.
    """
    try:
        user_id = get_jwt_identity()
        buyer = Buyer.query.get(user_id)
        
        if not buyer:
            return jsonify({"error": "Buyer not found"}), 404
        
        # Include details about orders
        orders = Order.query.filter_by(buyer_id=buyer.id).all()
        order_list = [
            {
                "id": order.id,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": order.created_at
            } for order in orders
        ]
        
        profile_data = {
            "name": buyer.name,
            "email": buyer.email,
            "phone_number": buyer.phone_number,
            "delivery_address": buyer.delivery_address,
            "orders": order_list
        }
        return jsonify(profile_data), 200
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@buyer_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update the profile of the logged-in buyer.
    """
    try:
        user_id = get_jwt_identity()
        buyer = Buyer.query.get(user_id)
        
        if not buyer:
            return jsonify({"error": "Buyer not found"}), 404
        
        data = request.json
        
        # Email validation
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({"error": "Invalid email format"}), 400
            buyer.email = data['email']
        
        # Phone number validation
        if 'phone_number' in data:
            if not validate_phone_number(data['phone_number']):
                return jsonify({"error": "Invalid phone number format"}), 400
            buyer.phone_number = data['phone_number']
        
        # Update other profile fields
        buyer.name = data.get('name', buyer.name)
        buyer.delivery_address = data.get('delivery_address', buyer.delivery_address)

        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email or phone number already in use"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating profile: {str(e)}"}), 500
