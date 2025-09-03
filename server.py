from flask import Flask
from flask_socketio import SocketIO, send
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "nam2010-secret"

# Redis Upstash URL từ biến môi trường
REDIS_URL = os.getenv("REDIS_URL")

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet",
    message_queue=REDIS_URL
)

@app.route("/")
def home():
    return "🚀 Chat Server đang chạy!"

@socketio.on("message")
def handle_message(msg):
    print("📩", msg)
    send(msg, broadcast=True)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
