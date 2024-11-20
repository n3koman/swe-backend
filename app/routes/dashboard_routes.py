from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Farmer, Buyer, Product, Order, Role

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    Retrieve dashboard data for the authenticated user based on their role.
    """
    try:
        # Get the current user identity from the JWT
        user_id = get_jwt_identity()

        # Fetch user details from the database
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Determine the role and fetch respective dashboard data
        if user.role == Role.ADMINISTRATOR:
            return get_admin_dashboard()

        elif user.role == Role.FARMER:
            return get_farmer_dashboard(user_id)

        elif user.role == Role.BUYER:
            return get_buyer_dashboard(user_id)

        else:
            return jsonify({"error": "Invalid role"}), 400

    except Exception as e:
        print(f"Error in get_dashboard: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


def get_admin_dashboard():
    """
    Retrieve the dashboard data for the administrator with detailed information.
    """
    try:
        # Gather detailed admin-specific data
        users = User.query.all()
        farmers = Farmer.query.all()
        buyers = Buyer.query.all()
        products = Product.query.all()
        orders = Order.query.all()

        # Collect user details
        user_data = [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at,
            }
            for user in users
        ]

        # Collect farmer details with their products
        farmer_data = [
            {
                "id": farmer.id,
                "name": farmer.name,
                "email": farmer.email,
                "farm_address": farmer.farm_address,
                "farm_size": farmer.farm_size,
                "crops": farmer.crop_types,
                "products": [
                    {
                        "id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "stock": product.stock,
                        "description": product.description,
                    }
                    for product in Product.query.filter_by(farmer_id=farmer.id).all()
                ],
            }
            for farmer in farmers
        ]

        # Collect buyer details with their orders
        buyer_data = [
            {
                "id": buyer.id,
                "name": buyer.name,
                "email": buyer.email,
                "delivery_address": buyer.delivery_address,
                "orders": [
                    {
                        "id": order.id,
                        "status": order.status,
                        "total_price": order.total_price,
                        "created_at": order.created_at,
                    }
                    for order in Order.query.filter_by(buyer_id=buyer.id).all()
                ],
            }
            for buyer in buyers
        ]

        # Collect product details
        product_data = [
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "stock": product.stock,
                "farmer_id": product.farmer_id,
            }
            for product in products
        ]

        # Collect order details
        order_data = [
            {
                "id": order.id,
                "buyer_id": order.buyer_id,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": order.created_at,
            }
            for order in orders
        ]

        dashboard_data = {
            "total_users": len(users),
            "total_farmers": len(farmers),
            "total_buyers": len(buyers),
            "total_products": len(products),
            "total_orders": len(orders),
            "users": user_data,
            "farmers": farmer_data,
            "buyers": buyer_data,
            "products": product_data,
            "orders": order_data,
        }

        return jsonify({"dashboard": "Administrator Dashboard", "data": dashboard_data}), 200

    except Exception as e:
        print(f"Error in get_admin_dashboard: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

def get_farmer_dashboard(user_id):
    """
    Retrieve the dashboard data for a farmer.
    """
    farmer = Farmer.query.get(user_id)
    if not farmer:
        return jsonify({"error": "Farmer data not found"}), 404

    # Gather farmer-specific dashboard data
    dashboard_data = {
        "name": farmer.name,
        "email": farmer.email,
        "farm_address": farmer.farm_address,
        "farm_size": farmer.farm_size,
        "crops": farmer.crop_types,
        "gov_id": farmer.gov_id,
        "products": [
            product.to_dict() for product in Product.query.filter_by(farmer_id=farmer.id).all()
        ]
    }
    return jsonify({"dashboard": "Farmer Dashboard", "data": dashboard_data}), 200


def get_buyer_dashboard(user_id):
    """
    Retrieve the dashboard data for a buyer.
    """
    buyer = Buyer.query.get(user_id)
    if not buyer:
        return jsonify({"error": "Buyer data not found"}), 404

    # Gather buyer-specific dashboard data
    dashboard_data = {
        "name": buyer.name,
        "email": buyer.email,
        "delivery_address": buyer.delivery_address,
        "orders": [
            order.to_dict() for order in Order.query.filter_by(buyer_id=buyer.id).all()
        ]
    }
    return jsonify({"dashboard": "Buyer Dashboard", "data": dashboard_data}), 200
