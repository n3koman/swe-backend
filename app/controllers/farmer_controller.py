# controllers/farmer_controller.py

from services.farmer_service import (
    get_farmer_profile,
    update_farmer_profile,
    add_product_listing,
    get_all_farm_products
)

# Get farmer profile
def retrieve_farmer_profile(farmer_id):
    return get_farmer_profile(farmer_id)

# Update farmer profile
def modify_farmer_profile(farmer_id, update_data):
    return update_farmer_profile(farmer_id, update_data)

# Add a product listing for a farmer
def create_product(farmer_id, product_data):
    return add_product_listing(farmer_id, product_data)

# Get all products listed by the farmer
def retrieve_farm_products(farmer_id):
    return get_all_farm_products(farmer_id)
