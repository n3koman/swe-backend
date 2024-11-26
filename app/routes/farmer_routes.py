from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Farmer, Resource, Product, ProductImage, db
from sqlalchemy.exc import IntegrityError
import re

farmer_bp = Blueprint("farmer", __name__)


def validate_email(email):
    """Validate email format"""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


def validate_phone_number(phone_number):
    """Validate phone number format"""
    phone_regex = r"^\+?1?\d{10,14}$"
    return re.match(phone_regex, phone_number) is not None


def validate_positive_number(value):
    return isinstance(value, (int, float)) and value >= 0


@farmer_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """
    Retrieve the profile of the logged-in farmer.
    """
    try:
        user_id = get_jwt_identity()
        farmer = Farmer.query.get(user_id)

        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404

        # Include additional details about farm and resources
        resources = Resource.query.filter_by(farmer_id=farmer.id).all()
        resource_list = [
            {
                "id": resource.id,
                "type": resource.resource_type,
                "description": resource.description,
                "quantity": resource.quantity,
            }
            for resource in resources
        ]

        profile_data = {
            "name": farmer.name,
            "email": farmer.email,
            "phone_number": farmer.phone_number,
            "farm_address": farmer.farm_address,
            "farm_size": farmer.farm_size,
            "crop_types": farmer.crop_types,
            "resources": resource_list,
        }
        return jsonify(profile_data), 200
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@farmer_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Update the profile of the logged-in farmer.
    """
    try:
        user_id = get_jwt_identity()
        farmer = Farmer.query.get(user_id)

        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404

        data = request.json

        # Email validation
        if "email" in data:
            if not validate_email(data["email"]):
                return jsonify({"error": "Invalid email format"}), 400
            farmer.email = data["email"]

        # Phone number validation
        if "phone_number" in data:
            if not validate_phone_number(data["phone_number"]):
                return jsonify({"error": "Invalid phone number format"}), 400
            farmer.phone_number = data["phone_number"]

        # Update other profile fields
        farmer.name = data.get("name", farmer.name)
        farmer.farm_address = data.get("farm_address", farmer.farm_address)
        farmer.farm_size = data.get("farm_size", farmer.farm_size)
        farmer.crop_types = data.get("crop_types", farmer.crop_types)

        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email or phone number already in use"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating profile: {str(e)}"}), 500


@farmer_bp.route("/resources", methods=["POST"])
@jwt_required()
def add_resource():
    """
    Add a new resource for the farmer.
    """
    try:
        user_id = get_jwt_identity()
        farmer = Farmer.query.get(user_id)

        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404

        data = request.json

        # Validate required fields
        if not all(key in data for key in ["resource_type", "description", "quantity"]):
            return jsonify({"error": "Missing required resource details"}), 400

        new_resource = Resource(
            farmer_id=farmer.id,
            resource_type=data["resource_type"],
            description=data["description"],
            quantity=data["quantity"],
        )

        db.session.add(new_resource)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Resource added successfully!",
                    "resource": {
                        "id": new_resource.id,
                        "type": new_resource.resource_type,
                        "description": new_resource.description,
                        "quantity": new_resource.quantity,
                    },
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error adding resource: {str(e)}"}), 500


@farmer_bp.route("/product", methods=["POST"])
@jwt_required()
def add_product():
    """
    Add a new product listing for the farmer.
    """
    try:
        user_id = get_jwt_identity()
        farmer = Farmer.query.get(user_id)
        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404

        data = request.json
        name = data.get("name")
        category = data.get("category")
        price = data.get("price")
        stock = data.get("stock")
        description = data.get("description")
        images = data.get("images", [])

        # Validate inputs
        if not all([name, category, price, stock]):
            return jsonify({"error": "Missing required fields"}), 400
        if not validate_positive_number(price) or not validate_positive_number(stock):
            return jsonify({"error": "Price and stock must be positive numbers"}), 400

        product = Product(
            name=name,
            category=category,
            price=price,
            stock=stock,
            description=description,
            farmer_id=farmer.id,
        )
        db.session.add(product)
        db.session.flush()  # Get product ID

        # Add images
        for image_url in images:
            product_image = ProductImage(product_id=product.id, image_url=image_url)
            db.session.add(product_image)

        db.session.commit()
        return (
            jsonify(
                {"message": "Product added successfully", "product_id": product.id}
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@farmer_bp.route("/product/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    """
    Update an existing product listing.
    """
    try:
        user_id = get_jwt_identity()
        product = Product.query.filter_by(id=product_id, farmer_id=user_id).first()
        if not product:
            return jsonify({"error": "Product not found or unauthorized access"}), 404

        data = request.json
        product.name = data.get("name", product.name)
        product.category = data.get("category", product.category)
        product.price = data.get("price", product.price)
        product.stock = data.get("stock", product.stock)
        product.description = data.get("description", product.description)

        if product.price <= 0 or product.stock < 0:
            return jsonify({"error": "Price and stock must be positive numbers"}), 400

        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@farmer_bp.route("/product/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    """
    Delete a product listing.
    """
    try:
        user_id = get_jwt_identity()
        product = Product.query.filter_by(id=product_id, farmer_id=user_id).first()
        if not product:
            return jsonify({"error": "Product not found or unauthorized access"}), 404

        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
