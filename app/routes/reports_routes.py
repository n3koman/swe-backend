from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import Farmer, Buyer, Order, Product

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/farmer/report", methods=["POST"])
@jwt_required()
def generate_farmer_report():
    """
    Generate sales or inventory report for a farmer.
    """
    farmer_id = get_jwt_identity()  # Get farmer ID from JWT
    data = request.json
    report_type = data.get("report_type", "sales")  # Default to sales
    date_range = data.get("date_range", [])

    try:
        # Validate farmer
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404

        start_date = datetime.fromisoformat(date_range[0]) if date_range else None
        end_date = datetime.fromisoformat(date_range[1]) if date_range else None

        if report_type == "sales":
            # Query orders for this farmer within the date range
            orders = (
                Order.query.join(Order.order_items)
                .join(Product)
                .filter(Product.farmer_id == farmer_id)
                .filter(Order.created_at.between(start_date, end_date))
                .all()
            )

            report_data = {
                "total_revenue": sum(order.total_price for order in orders),
                "total_orders": len(orders),
                "product_sales": [
                    {
                        "product_name": item.product_name,
                        "quantity_sold": sum(
                            item.quantity
                            for item in order.order_items
                            if item.product_id == product.id
                        ),
                    }
                    for product in farmer.products
                    for order in orders
                    for item in order.order_items
                ],
            }

        elif report_type == "inventory":
            # Compile inventory data for the farmer
            report_data = [
                {
                    "product_name": product.name,
                    "stock": product.stock,
                    "restocking_alert": product.stock < 10,  # Example threshold
                }
                for product in farmer.products
            ]
        else:
            return jsonify({"error": "Invalid report type"}), 400

        return jsonify({"data": report_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/buyer/report", methods=["POST"])
@jwt_required()
def generate_buyer_report():
    """
    Generate purchasing habit report for a buyer.
    """
    buyer_id = get_jwt_identity()  # Get buyer ID from JWT
    data = request.json
    date_range = data.get("date_range", [])

    try:
        # Validate buyer
        buyer = Buyer.query.get(buyer_id)
        if not buyer:
            return jsonify({"error": "Buyer not found"}), 404

        start_date = datetime.fromisoformat(date_range[0]) if date_range else None
        end_date = datetime.fromisoformat(date_range[1]) if date_range else None

        # Query orders for this buyer within the date range
        orders = (
            Order.query.filter_by(buyer_id=buyer_id)
            .filter(Order.created_at.between(start_date, end_date))
            .all()
        )

        # Compile report data
        report_data = {
            "total_spent": sum(order.total_price for order in orders),
            "total_orders": len(orders),
            "preferred_products": [
                {
                    "product_name": item.product_name,
                    "total_spent": sum(
                        item.total_price
                        for item in order.order_items
                        if item.product_name == item.product_name
                    ),
                }
                for order in orders
                for item in order.order_items
            ],
        }

        return jsonify({"data": report_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
