from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Chat, Message, User, Farmer, Buyer
from datetime import datetime

chat_bp = Blueprint("chat", __name__)

# Endpoint to start a new chat
@chat_bp.route("/start-chat", methods=["POST"])
@jwt_required()
def start_chat():
    """
    Start a new chat between a buyer and a farmer.
    """
    data = request.json
    farmer_id = data.get("farmer_id")
    buyer_id = get_jwt_identity()

    if not farmer_id:
        return jsonify({"error": "Farmer ID is required"}), 400

    # Check if chat already exists
    chat = Chat.query.filter_by(buyer_id=buyer_id, farmer_id=farmer_id).first()
    if not chat:
        chat = Chat(buyer_id=buyer_id, farmer_id=farmer_id)
        db.session.add(chat)
        db.session.commit()

    return jsonify({"chat_id": chat.id}), 201


# Endpoint to send a message
@chat_bp.route("/chat/<int:chat_id>/message", methods=["POST"])
@jwt_required()
def send_message(chat_id):
    """
    Send a message within a specific chat.
    """
    data = request.json
    sender_id = get_jwt_identity()
    content = data.get("content")

    if not content:
        return jsonify({"error": "Message content is required"}), 400

    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    # Ensure the sender is part of the chat
    if sender_id not in [chat.buyer_id, chat.farmer_id]:
        return jsonify({"error": "Unauthorized"}), 403

    message = Message(chat_id=chat_id, sender_id=sender_id, content=content)
    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201


# Endpoint to fetch messages in a chat
@chat_bp.route("/chat/<int:chat_id>/messages", methods=["GET"])
@jwt_required()
def get_chat_messages(chat_id):
    """
    Get all messages within a specific chat.
    """
    user_id = get_jwt_identity()
    chat = Chat.query.get(chat_id)

    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    # Ensure the user is part of the chat
    if user_id not in [chat.buyer_id, chat.farmer_id]:
        return jsonify({"error": "Unauthorized"}), 403

    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    return jsonify({"messages": [message.to_dict() for message in messages]}), 200


# Endpoint to get all chats for a user
@chat_bp.route("/chats", methods=["GET"])
@jwt_required()
def get_user_chats():
    """
    Get all chats for the logged-in user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Retrieve chats where the user is either a buyer or a farmer
    if isinstance(user, Farmer):
        chats = Chat.query.filter_by(farmer_id=user_id).all()
    elif isinstance(user, Buyer):
        chats = Chat.query.filter_by(buyer_id=user_id).all()
    else:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify({"chats": [chat.to_dict() for chat in chats]}), 200
