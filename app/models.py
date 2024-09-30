from app import db
from sqlalchemy import Enum
import enum

class Role(enum.Enum):
    FARMER = 'farmer'
    BUYER = 'buyer'
    ADMINISTRATOR = 'administrator'

class OrderStatus(enum.Enum):
    PLACED = 'placed'
    PROCESSING = 'processing'
    DISPATCHED = 'dispatched'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'

class DeliveryMethod(enum.Enum):
    HOME_DELIVERY = 'home_delivery'
    PICKUP_POINT = 'pickup_point'
    THIRD_PARTY = 'third_party'

class DeliveryStatus(enum.Enum):
    NOT_SHIPPED = 'not_shipped'
    SHIPPED = 'shipped'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    role = db.Column(db.Enum(Role), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    __mapper_args__ = {'polymorphic_on': role}

class Farmer(User):
    __tablename__ = 'farmers'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    farm_name = db.Column(db.String(100), nullable=False)
    farm_location = db.Column(db.String(255))
    farm_size = db.Column(db.Float)
    crop_types = db.Column(db.ARRAY(db.String))
    resources = db.relationship('Resource', backref='farmer')

    __mapper_args__ = {'polymorphic_identity': Role.FARMER}

class Buyer(User):
    __tablename__ = 'buyers'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    delivery_address = db.Column(db.String(255))

    __mapper_args__ = {'polymorphic_identity': Role.BUYER}

class Administrator(User):
    __tablename__ = 'administrators'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    admin_level = db.Column(db.Integer)

    __mapper_args__ = {'polymorphic_identity': Role.ADMINISTRATOR}

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Delivery(db.Model):
    __tablename__ = 'deliveries'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(50), default='in transit')  # 'in transit', 'delivered'
    tracking_number = db.Column(db.String(100), nullable=True)
    estimated_delivery_date = db.Column(db.DateTime, nullable=True)


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    description = db.Column(db.String(255))
    resource_type = db.Column(db.String(100))
