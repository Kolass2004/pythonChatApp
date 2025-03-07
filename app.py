from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Track active users
active_users = set()
typing_users = set()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('user_count', {'count': len(active_users)}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")
    emit('user_count', {'count': len(active_users)}, broadcast=True)

@socketio.on('chat')
def handle_chat(data):
    # data is expected to be a dict with 'username', 'message', and 'timestamp'
    print(f"Message from {data['username']}: {data['message']}")
    
    # Add server timestamp if not provided
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
        
    # Broadcast the message to all connected clients
    emit('message', data, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    typing_users.add(data['username'])
    emit('user-typing', data, broadcast=True)

@socketio.on('stop-typing')
def handle_stop_typing(data):
    if data['username'] in typing_users:
        typing_users.remove(data['username'])
    emit('user-stop-typing', {}, broadcast=True)

@socketio.on('join')
def handle_join(data):
    active_users.add(data['username'])
    emit('user_joined', {
        'username': data['username'],
        'count': len(active_users)
    }, broadcast=True)

@socketio.on('leave')
def handle_leave(data):
    if data['username'] in active_users:
        active_users.remove(data['username'])
    emit('user_left', {
        'username': data['username'],
        'count': len(active_users)
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)