from flask_socketio import emit, join_room
from app.models import Chat, Message, db

def register_socket_events(socketio):
    @socketio.on("join_room")
    def handle_join_room(data):
        room = f"chat_{data['chat_id']}"
        join_room(room)
        emit("room_joined", {"chat_id": data['chat_id']}, room=room)

    @socketio.on("send_message")
    def handle_send_message(data):
        chat_id = data['chat_id']
        sender_id = data['sender_id']
        content = data['message']

        # Save message to database
        new_message = Message(chat_id=chat_id, sender_id=sender_id, content=content)
        db.session.add(new_message)
        db.session.commit()

        # Broadcast the message to the room
        room = f"chat_{chat_id}"
        emit("receive_message", new_message.to_dict(), room=room)
