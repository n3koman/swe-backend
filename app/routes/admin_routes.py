from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Farmer, Buyer, Product, Order, ProductImage, db
from sqlalchemy.exc import IntegrityError
import base64

admin_bp = Blueprint("admin", __name__)


def is_admin(user_id):
    """
    Utility function to check if the user is an admin.
    """
    user = User.query.get(user_id)
    return str(user.role) == "Role.ADMINISTRATOR"  # Ensures role is checked as string


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """
    Retrieve all users (farmers, buyers, admins).
    """
    try:
        admin_id = get_jwt_identity()
        if not is_admin(admin_id):
            return jsonify({"error": "Unauthorized access"}), 403

        all_users = User.query.all()
        user_list = [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": str(user.role),
                "created_at": user.created_at.isoformat(),
            }
            for user in all_users
        ]
        return jsonify({"users": user_list}), 200
    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@admin_bp.route("/user/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """
    Update a user's profile.
    """
    try:
        admin_id = get_jwt_identity()
        if not is_admin(admin_id):
            return jsonify({"error": "Unauthorized access"}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        user.role = data.get("role", user.role)  # Allow admin to update roles

        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already in use"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@admin_bp.route("/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """
    Delete a user.
    """
    try:
        admin_id = get_jwt_identity()
        if not is_admin(admin_id):
            return jsonify({"error": "Unauthorized access"}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@admin_bp.route("/products", methods=["GET"])
@jwt_required()
def get_products():
    """
    Retrieve all products with their images and categories.
    """
    try:
        admin_id = get_jwt_identity()
        if not is_admin(admin_id):
            return jsonify({"error": "Unauthorized access"}), 403

        products = Product.query.all()
        product_list = []
        for product in products:
            images = ProductImage.query.filter_by(product_id=product.id).all()
            image_list = [
                {
                    "mime_type": image.mime_type,
                    "image_data": base64.b64encode(image.image_data).decode("utf-8"),
                }
                for image in images
            ]
            product_list.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,  # Assuming category is a field in the Product model
                    "price": product.price,
                    "stock": product.stock,
                    "description": product.description,
                    "farmer_id": product.farmer_id,
                    "images": image_list,
                }
            )

        return jsonify({"products": product_list}), 200
    except Exception as e:
        print(f"Error in get_products: {e}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@admin_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    """
    Retrieve all orders.
    """
    try:
        admin_id = get_jwt_identity()
        if not is_admin(admin_id):
            return jsonify({"error": "Unauthorized access"}), 403

        orders = Order.query.all()
        order_list = [
            {
                "id": order.id,
                "buyer_id": order.buyer_id,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": order.created_at.isoformat(),
            }
            for order in orders
        ]
        return jsonify({"orders": order_list}), 200
    except Exception as e:
        print(f"Error in get_orders: {e}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@admin_bp.route("/product/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    """
    Delete a product.
    """
    try:
        admin_id = get_jwt_identity()
        if not is_admin(admin_id):
            return jsonify({"error": "Unauthorized access"}), 403

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


@admin_bp.route("/order/<int:order_id>", methods=["DELETE"])
@jwt_required()
def delete_order(order_id):
    """
    Delete an order.
    """
    try:
        admin_id = get_jwt_identity()
        if not is_admin(admin_id):
            return jsonify({"error": "Unauthorized access"}), 403

        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
