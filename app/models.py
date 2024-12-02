from app import db
from sqlalchemy import (
    Enum,
    Float,
    Integer,
    String,
    DateTime,
    Text,
    LargeBinary,
    ForeignKey,
)
import enum
from datetime import datetime
import base64


# Enum Classes for Choices
class Role(enum.Enum):
    FARMER = "farmer"
    BUYER = "buyer"
    ADMINISTRATOR = "administrator"


class OrderStatus(enum.Enum):
    PLACED = "placed"
    PROCESSING = "processing"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class DeliveryMethod(enum.Enum):
    HOME_DELIVERY = "home_delivery"
    PICKUP_POINT = "pickup_point"
    THIRD_PARTY = "third_party"


class DeliveryStatus(enum.Enum):
    NOT_SHIPPED = "not_shipped"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


# Base User Model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password = db.Column(String(255), nullable=False)
    phone_number = db.Column(String(15), unique=True, nullable=True)
    role = db.Column(Enum(Role), nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, onupdate=datetime.utcnow)

    __mapper_args__ = {"polymorphic_on": role}


# Farmer Model with Farm Details
class Farmer(User):
    __tablename__ = "farmers"
    id = db.Column(Integer, db.ForeignKey("users.id"), primary_key=True)
    farm_address = db.Column(db.String(255), nullable=False)
    farm_size = db.Column(Float, nullable=True)
    crop_types = db.Column(db.ARRAY(String), nullable=True)
    gov_id = db.Column(String(50), nullable=True)  # Government-issued ID
    products = db.relationship("Product", backref="farmer", lazy=True)

    __mapper_args__ = {"polymorphic_identity": Role.FARMER}


# Buyer Model with Delivery Preferences
class Buyer(User):
    __tablename__ = "buyers"
    id = db.Column(Integer, db.ForeignKey("users.id"), primary_key=True)
    delivery_address = db.Column(String(255), nullable=False)
    preferred_payment_method = db.Column(String(50), nullable=True)
    orders = db.relationship("Order", backref="buyer", lazy=True)

    __mapper_args__ = {"polymorphic_identity": Role.BUYER}


# Administrator Model (Simplified, more attributes can be added)
class Administrator(User):
    __tablename__ = "administrators"
    id = db.Column(Integer, db.ForeignKey("users.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": Role.ADMINISTRATOR}


# Product Model for Farmer's Products
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    category = db.Column(String(100), nullable=False)
    price = db.Column(Float, nullable=False)
    stock = db.Column(Integer, nullable=False)
    description = db.Column(Text, nullable=True)
    farmer_id = db.Column(Integer, db.ForeignKey("farmers.id"), nullable=False)
    images = db.relationship(
        "ProductImage", backref="product", lazy=True, cascade="all, delete-orphan"
    )

    created_at = db.Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "description": self.description,
            "created_at": self.created_at,
            "images": [image.to_dict() for image in self.images],
        }


class ProductImage(db.Model):
    __tablename__ = "product_images"
    id = db.Column(Integer, primary_key=True)
    product_id = db.Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    image_data = db.Column(LargeBinary, nullable=False)  # Binary image data
    mime_type = db.Column(
        String(50), nullable=False
    )  # Image MIME type (e.g., 'image/png')
    created_at = db.Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "mime_type": self.mime_type,
        }


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(Integer, primary_key=True)
    buyer_id = db.Column(Integer, db.ForeignKey("buyers.id"), nullable=False)
    status = db.Column(Enum(OrderStatus), default=OrderStatus.PLACED, nullable=False)
    total_price = db.Column(Float, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, onupdate=datetime.utcnow)
    order_items = db.relationship(
        "OrderItem", backref="order", lazy=True, cascade="all, delete-orphan"
    )
    delivery = db.relationship(
        "Delivery", backref="order", uselist=False
    )  # One-to-one with Delivery

    def to_dict(self):
        return {
            "id": self.id,
            "buyer_id": self.buyer_id,
            "status": self.status.value,
            "total_price": self.total_price,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "order_items": [item.to_dict() for item in self.order_items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(String(100), nullable=False)
    product_price = db.Column(Float, nullable=False)
    quantity = db.Column(Integer, nullable=False)
    total_price = db.Column(Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_price": self.product_price,
            "quantity": self.quantity,
            "total_price": self.total_price,
        }


# Delivery Model for delivery tracking
class Delivery(db.Model):
    __tablename__ = "deliveries"
    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, db.ForeignKey("orders.id"), nullable=False)
    delivery_method = db.Column(Enum(DeliveryMethod), nullable=False)
    status = db.Column(
        Enum(DeliveryStatus), default=DeliveryStatus.NOT_SHIPPED, nullable=False
    )
    tracking_number = db.Column(String(100), nullable=True)
    estimated_delivery_date = db.Column(DateTime, nullable=True)
    address = db.Column(String(255), nullable=False)
    country = db.Column(String(100), nullable=False)  # Add this field
    special_instructions = db.Column(String(255), nullable=True)


# Resource Model for managing farmer resources
class Resource(db.Model):
    __tablename__ = "resources"
    id = db.Column(Integer, primary_key=True)
    farmer_id = db.Column(Integer, db.ForeignKey("farmers.id"), nullable=False)
    description = db.Column(String(255), nullable=True)
    resource_type = db.Column(
        String(100), nullable=False
    )  # E.g., seeds, pesticides, equipment
    stock = db.Column(Integer, nullable=True)


class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("buyers.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)  # Add this field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship("Product", backref="cart_items")
    buyer = db.relationship("Buyer", backref="cart_items")

    def to_dict(self):
        return {
            "id": self.product_id,  # Use product ID for consistency
            "product_id": self.product_id,
            "name": self.product.name,  # Add name
            "price": self.product.price,
            "quantity": self.quantity,
            "images": [
                {
                    "data": base64.b64encode(image.image_data).decode("utf-8"),
                    "mime_type": image.mime_type,
                }
                for image in self.product.images
            ],
            "farmer_name": (
                self.product.farmer.name if self.product.farmer else "Unknown"
            ),
            "total_price": self.quantity * self.product.price,
        }


class Chat(db.Model):
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("buyers.id"), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = db.relationship(
        "Message", backref="chat", lazy=True, cascade="all, delete-orphan"
    )

    # Relationship to farmer
    farmer = db.relationship("Farmer", backref="chats", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "buyer_id": self.buyer_id,
            "farmer_id": self.farmer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "messages": [message.to_dict() for message in self.messages],
        }


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("chats.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
