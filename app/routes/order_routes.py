from flask import Blueprint, jsonify

order_bp = Blueprint('order', __name__)

@order_bp.route('/orders', methods=['GET'])
def get_orders():
    return jsonify({"message": "List of orders"})
