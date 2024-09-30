from flask import Blueprint, jsonify

# Define the blueprint
product_bp = Blueprint('product', __name__)

# Example route for product listing
@product_bp.route('/products', methods=['GET'])
def get_products():
    return jsonify({"message": "List of products"})
