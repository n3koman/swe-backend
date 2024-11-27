from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Buyer, Order, Farmer, Product, db
from sqlalchemy.exc import IntegrityError
import re
import base64
import difflib

buyer_bp = Blueprint("buyer", __name__)


def validate_email(email):
    """Validate email format"""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


def validate_phone_number(phone_number):
    """Validate phone number format"""
    phone_regex = r"^\+?1?\d{10,14}$"
    return re.match(phone_regex, phone_number) is not None


@buyer_bp.route("/profile", methods=["GET"])
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
                "created_at": order.created_at,
            }
            for order in orders
        ]

        profile_data = {
            "name": buyer.name,
            "email": buyer.email,
            "phone_number": buyer.phone_number,
            "delivery_address": buyer.delivery_address,
            "orders": order_list,
        }
        return jsonify(profile_data), 200
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@buyer_bp.route("/profile", methods=["PUT"])
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
        if "email" in data:
            if not validate_email(data["email"]):
                return jsonify({"error": "Invalid email format"}), 400
            buyer.email = data["email"]

        # Phone number validation
        if "phone_number" in data:
            if not validate_phone_number(data["phone_number"]):
                return jsonify({"error": "Invalid phone number format"}), 400
            buyer.phone_number = data["phone_number"]

        # Update other profile fields
        buyer.name = data.get("name", buyer.name)
        buyer.delivery_address = data.get("delivery_address", buyer.delivery_address)

        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email or phone number already in use"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating profile: {str(e)}"}), 500


@buyer_bp.route("/products", methods=["GET"])
@jwt_required()
def get_products():
    """
    Fetch products with optional search, filtering, and 'Did you mean' suggestions.
    """
    try:
        # Retrieve query parameters
        search_query = request.args.get("search", "").strip()
        category = request.args.get("category", "").strip()
        farmer_id = request.args.get("farmer", "").strip()
        price_min = request.args.get("price_min", "").strip()
        price_max = request.args.get("price_max", "").strip()
        sort_by_price = request.args.get("sort", "").strip()  # 'asc' or 'desc'

        # Base query
        query = Product.query

        # Apply search and filters
        if search_query:
            query = query.filter(Product.name.ilike(f"%{search_query}%"))
        if category:
            query = query.filter(Product.category == category)
        if farmer_id:
            query = query.filter(Product.farmer_id == int(farmer_id))
        if price_min:
            query = query.filter(Product.price >= float(price_min))
        if price_max:
            query = query.filter(Product.price <= float(price_max))

        # Apply sorting by price
        if sort_by_price.lower() == "asc":
            query = query.order_by(Product.price.asc())
        elif sort_by_price.lower() == "desc":
            query = query.order_by(Product.price.desc())

        # Fetch products
        products = query.all()

        # If no products found
        if not products and search_query:
            # Fetch all product names for suggestion
            all_product_names = [p.name for p in Product.query.all()]

            # Find close matches using difflib
            suggestions = difflib.get_close_matches(
                search_query, all_product_names, n=5, cutoff=0.6
            )

            if suggestions:
                return (
                    jsonify(
                        {
                            "message": "No exact products found. Did you mean:",
                            "suggestions": suggestions,
                        }
                    ),
                    404,
                )

            return jsonify({"message": "No products found"}), 404

        # Serialize product data
        product_list = [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "price": float(product.price),
                "stock": int(product.stock),
                "farmer_id": product.farmer_id,
                "farmer_name": product.farmer.name if product.farmer else None,
                "images": (
                    [
                        {
                            "mime_type": image.mime_type,
                            "data": base64.b64encode(image.image_data).decode("utf-8"),
                        }
                        for image in product.images
                    ]
                    if hasattr(product, "images") and product.images
                    else []
                ),
            }
            for product in products
        ]

        # Return serialized products
        return jsonify({"products": product_list}), 200

    except Exception as e:
        print(f"ERROR: Exception occurred - {str(e)}")
        return jsonify({"error": f"Error fetching products: {str(e)}"}), 500
