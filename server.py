import os, json, datetime
import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import redis

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "chat-secret")

# === Redis Upstash (bắt buộc) ===
REDIS_URL = os.getenv("REDIS_URL")  # ví dụ: rediss://default:TOKEN@xxx.upstash.io:6379
if not REDIS_URL:
    raise RuntimeError("Missing REDIS_URL env. Set rediss://... from Upstash!")

# redis client (decode strings)
r = redis.from_url(REDIS_URL, decode_responses=True)

# SocketIO + Redis message queue để sync 5 VPS
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet",
    message_queue=REDIS_URL
)

# === Config lưu lịch sử ===
LIST_KEY = "chat:messages"
MAX_MSGS = 500  # giữ tối đa 500 tin

def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_message(packet: dict):
    # packet = {"user": "...", "msg": "...", "time": "..."}
    r.rpush(LIST_KEY, json.dumps(packet))
    r.ltrim(LIST_KEY, -MAX_MSGS, -1)

def get_history(limit: int = 50):
    limit = max(1, min(limit, MAX_MSGS))
    items = r.lrange(LIST_KEY, -limit, -1)  # lấy cuối danh sách
    return [json.loads(x) for x in items]

@app.route("/")
def home():
    return "🚀 Chat Server OK (Redis Upstash + Socket.IO) — /history to fetch logs"

@app.route("/health")
def health():
    try:
        r.ping()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "redis_error", "detail": str(e)}, 500

@app.route("/history")
def history():
    try:
        limit = int(request.args.get("limit", "50"))
    except ValueError:
        limit = 50
    return jsonify(get_history(limit))

@socketio.on("message")
def handle_message(data):
    # data expected: {"user": "...", "msg": "..."}
    if not isinstance(data, dict) or "user" not in data or "msg" not in data:
        # fallback: nếu client cũ gửi chuỗi "user: msg"
        if isinstance(data, str) and ":" in data:
            u, m = data.split(":", 1)
            data = {"user": u.strip(), "msg": m.strip()}
        else:
            return  # bỏ qua gói không hợp lệ

    packet = {"user": str(data["user"])[:50], "msg": str(data["msg"])[:2000], "time": now_str()}
    save_message(packet)
    emit("message", packet, broadcast=True)  # broadcast cho mọi client mọi VPS

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)

