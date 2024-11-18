# services/farmer_service.py

from app.models import Farmer, Product, db
from sqlalchemy.exc import SQLAlchemyError

# Get farmer profile details
def get_farmer_profile(farmer_id):
    return Farmer.query.get(farmer_id)

# Update farmer profile details
def update_farmer_profile(farmer_id, update_data):
    try:
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return None
        for key, value in update_data.items():
            setattr(farmer, key, value)
        db.session.commit()
        return farmer
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

# Add a new product listing for a farmer
def add_product_listing(farmer_id, product_data):
    try:
        new_product = Product(farmer_id=farmer_id, **product_data)
        db.session.add(new_product)
        db.session.commit()
        return new_product
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

# Retrieve all products for a specific farmer
def get_all_farm_products(farmer_id):
    return Product.query.filter_by(farmer_id=farmer_id).all()
