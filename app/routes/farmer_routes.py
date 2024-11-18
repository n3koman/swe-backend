# routes/farmer_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from controllers.farmer_controller import (
    retrieve_farmer_profile,
    modify_farmer_profile,
    create_product,
    retrieve_farm_products
)

farmer_bp = Blueprint('farmer_bp', __name__)

@farmer_bp.route('/<int:farmer_id>/profile', methods=['GET'])
@jwt_required()
def get_farmer_profile(farmer_id):
    profile = retrieve_farmer_profile(farmer_id)
    if profile:
        return jsonify(profile), 200
    else:
        return jsonify({"error": "Farmer not found"}), 404

@farmer_bp.route('/<int:farmer_id>/profile', methods=['PUT'])
@jwt_required()
def update_farmer_profile(farmer_id):
    data = request.json
    updated_profile = modify_farmer_profile(farmer_id, data)
    if updated_profile:
        return jsonify(updated_profile), 200
    else:
        return jsonify({"error": "Update failed or farmer not found"}), 404

@farmer_bp.route('/<int:farmer_id>/products', methods=['POST'])
@jwt_required()
def add_product(farmer_id):
    product_data = request.json
    new_product = create_product(farmer_id, product_data)
    return jsonify(new_product), 201

@farmer_bp.route('/<int:farmer_id>/products', methods=['GET'])
@jwt_required()
def list_products(farmer_id):
    products = retrieve_farm_products(farmer_id)
    return jsonify(products), 200
