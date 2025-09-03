from flask import Flask, jsonify
from flask_socketio import SocketIO, send
import sqlite3
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "nam2010-secret"

# SQLite file
DB_FILE = "chat.db"

# setup socketio
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# init sqlite
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_message(msg):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (content) VALUES (?)", (msg,))
    conn.commit()
    conn.close()

def load_messages(limit=50):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT content, timestamp FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    # đảo ngược để tin nhắn cũ nhất nằm trên
    return [{"msg": row[0], "time": row[1]} for row in rows[::-1]]

@app.route("/")
def home():
    return "🚀 Chat Server đang chạy với SQLite!"

@app.route("/history")
def history():
    messages = load_messages()
    return jsonify(messages)

@socketio.on("message")
def handle_message(msg):
    print("📩", msg)
    save_message(msg)
    send(msg, broadcast=True)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)

