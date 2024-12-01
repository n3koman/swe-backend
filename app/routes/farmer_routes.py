from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    Farmer,
    Resource,
    Product,
    ProductImage,
    Order,
    OrderItem,
    OrderStatus,
    Message,
    Chat,
    db,
)
from sqlalchemy.exc import IntegrityError
import re
import base64

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
                "stock": resource.stock,
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
        if not all(key in data for key in ["resource_type", "description", "stock"]):
            return jsonify({"error": "Missing required resource details"}), 400

        new_resource = Resource(
            farmer_id=farmer.id,
            resource_type=data["resource_type"],
            description=data["description"],
            stock=data["stock"],
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
                        "stock": new_resource.stock,
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
        images = data.get("images", [])  # Base64 encoded image data

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

        # Save images to the database
        for image_base64 in images:
            try:
                image_data = base64.b64decode(image_base64)
                product_image = ProductImage(
                    product_id=product.id, image_data=image_data, mime_type="image/png"
                )
                db.session.add(product_image)
            except Exception as e:
                return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

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


# Update a product's images
@farmer_bp.route("/product/<int:product_id>/images", methods=["PUT"])
@jwt_required()
def update_product_images(product_id):
    """
    Update images for an existing product.
    """
    try:
        user_id = get_jwt_identity()
        product = Product.query.filter_by(id=product_id, farmer_id=user_id).first()
        if not product:
            return jsonify({"error": "Product not found or unauthorized access"}), 404

        data = request.json
        images = data.get("images", [])  # Base64 encoded image data

        # Delete existing images
        ProductImage.query.filter_by(product_id=product.id).delete()

        # Add new images
        for image_base64 in images:
            try:
                image_data = base64.b64decode(image_base64)
                product_image = ProductImage(
                    product_id=product.id, image_data=image_data, mime_type="image/png"
                )
                db.session.add(product_image)
            except Exception as e:
                return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

        db.session.commit()
        return jsonify({"message": "Product images updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


# Fetch images for a product
@farmer_bp.route("/product/<int:product_id>/images", methods=["GET"])
@jwt_required()
def get_product_images(product_id):
    """
    Get images for a specific product.
    """
    try:
        user_id = get_jwt_identity()
        product = Product.query.filter_by(id=product_id, farmer_id=user_id).first()
        if not product:
            return jsonify({"error": "Product not found or unauthorized access"}), 404

        images = ProductImage.query.filter_by(product_id=product.id).all()
        image_list = [
            {
                "id": img.id,
                "mime_type": img.mime_type,
                "image_data": base64.b64encode(img.image_data).decode("utf-8"),
            }
            for img in images
        ]
        return jsonify({"images": image_list}), 200

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


# Delete images for a product
@farmer_bp.route("/product/<int:product_id>/images", methods=["DELETE"])
@jwt_required()
def delete_product_images(product_id):
    """
    Delete all images for a specific product.
    """
    try:
        user_id = get_jwt_identity()
        product = Product.query.filter_by(id=product_id, farmer_id=user_id).first()
        if not product:
            return jsonify({"error": "Product not found or unauthorized access"}), 404

        ProductImage.query.filter_by(product_id=product.id).delete()
        db.session.commit()
        return jsonify({"message": "Product images deleted successfully"}), 200

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

        # Convert price and stock to the appropriate type and validate them
        price = data.get("price", product.price)
        stock = data.get("stock", product.stock)

        # Ensure price and stock are numbers
        try:
            if price is not None:
                price = float(price)
            if stock is not None:
                stock = int(stock)
        except ValueError:
            return (
                jsonify(
                    {"error": "Price must be a number and stock must be an integer"}
                ),
                400,
            )

        # Update the product
        product.name = data.get("name", product.name)
        product.category = data.get("category", product.category)
        product.price = price
        product.stock = stock
        product.description = data.get("description", product.description)

        # Validate price and stock
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


@farmer_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_farmer_orders():
    """
    Retrieve all orders that include products sold by the logged-in farmer.
    """
    try:
        # Get the farmer's ID from the JWT
        farmer_id = get_jwt_identity()

        # Validate that the user is a farmer
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return jsonify({"error": "Unauthorized access"}), 403

        # Get all products sold by the farmer
        farmer_products = Product.query.filter_by(farmer_id=farmer_id).all()
        product_ids = [product.id for product in farmer_products]

        # Query orders that include the farmer's products
        orders = (
            db.session.query(Order)
            .join(OrderItem)
            .filter(OrderItem.product_id.in_(product_ids))
            .distinct()
            .all()
        )

        # Serialize the orders with relevant details
        order_list = [
            {
                "order_id": order.id,
                "buyer_id": order.buyer_id,
                "status": order.status.value,
                "total_price": order.total_price,
                "created_at": order.created_at.isoformat(),
                "updated_at": (
                    order.updated_at.isoformat() if order.updated_at else None
                ),
                "order_items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "product_price": item.product_price,
                        "quantity": item.quantity,
                        "total_price": item.total_price,
                    }
                    for item in order.order_items
                    if item.product_id in product_ids
                ],
                "delivery": (
                    {
                        "id": order.delivery.id if order.delivery else None,
                        "delivery_method": (
                            order.delivery.delivery_method.value
                            if order.delivery
                            else None
                        ),
                        "status": (
                            order.delivery.status.value if order.delivery else None
                        ),
                        "tracking_number": (
                            order.delivery.tracking_number if order.delivery else None
                        ),
                        "estimated_delivery_date": (
                            order.delivery.estimated_delivery_date.isoformat()
                            if order.delivery and order.delivery.estimated_delivery_date
                            else None
                        ),
                        "address": order.delivery.address if order.delivery else None,
                        "country": order.delivery.country if order.delivery else None,
                        "special_instructions": (
                            order.delivery.special_instructions
                            if order.delivery
                            else None
                        ),
                    }
                    if order.delivery
                    else None
                ),
            }
            for order in orders
        ]

        return jsonify({"orders": order_list}), 200

    except Exception as e:
        print(f"Error in get_farmer_orders: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@farmer_bp.route("/orders/<int:order_id>/status", methods=["PATCH"])
@jwt_required()
def update_order_status(order_id):
    """
    Update the status of an order that includes products sold by the logged-in farmer.
    """
    try:
        farmer_id = get_jwt_identity()

        # Ensure the user is a farmer
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return jsonify({"error": "Unauthorized access"}), 403

        data = request.get_json()
        new_status = data.get("status")

        if not new_status or new_status not in OrderStatus.__members__:
            return jsonify({"error": "Invalid order status"}), 400

        # Fetch the order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Ensure the order contains products sold by the farmer
        farmer_product_ids = [
            product.id for product in Product.query.filter_by(farmer_id=farmer_id).all()
        ]
        order_product_ids = [item.product_id for item in order.order_items]

        if not any(pid in farmer_product_ids for pid in order_product_ids):
            return jsonify({"error": "Unauthorized to update this order"}), 403

        # Update the status
        order.status = OrderStatus[new_status]
        db.session.commit()

        return (
            jsonify(
                {"message": "Order status updated successfully", "order_id": order.id}
            ),
            200,
        )

    except Exception as e:
        print(f"Error in update_order_status: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@farmer_bp.route("/chats", methods=["GET"])
@jwt_required()
def list_chats():
    """
    List all chats for the authenticated farmer.
    """
    farmer_id = get_jwt_identity()
    chats = Chat.query.filter_by(farmer_id=farmer_id).all()

    chat_list = [
        {
            "id": chat.id,
            "buyer_id": chat.buyer_id,
            "buyer_name": chat.buyer.name if chat.buyer else "Unknown",
            "last_message": chat.messages[-1].content if chat.messages else None,
            "updated_at": chat.updated_at.isoformat() if chat.updated_at else None,
        }
        for chat in chats
    ]

    return jsonify({"chats": chat_list}), 200


# Endpoint to fetch messages for a specific chat
@farmer_bp.route("/chats/<int:chat_id>/messages", methods=["GET"])
@jwt_required()
def get_chat_messages(chat_id):
    """
    Retrieve all messages for a specific chat.
    """
    farmer_id = get_jwt_identity()
    chat = Chat.query.get(chat_id)

    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    # Verify that the farmer is part of the chat
    if chat.farmer_id != farmer_id:
        return jsonify({"error": "Unauthorized"}), 403

    messages = (
        Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    )
    return jsonify({"messages": [message.to_dict() for message in messages]}), 200


# Endpoint to send a message in a chat
@farmer_bp.route("/chats/<int:chat_id>/message", methods=["POST"])
@jwt_required()
def send_message(chat_id):
    """
    Send a message in a specific chat.
    """
    farmer_id = get_jwt_identity()
    data = request.json
    content = data.get("content")

    if not content:
        return jsonify({"error": "Message content is required"}), 400

    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    # Verify that the farmer is part of the chat
    if chat.farmer_id != farmer_id:
        return jsonify({"error": "Unauthorized"}), 403

    message = Message(chat_id=chat_id, sender_id=farmer_id, content=content)
    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201
