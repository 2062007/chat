import socketio, random
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from datetime import datetime

console = Console()

# Danh sách 5 VPS server (đổi URL Render của ông vào đây)
SERVERS = [
    "https://chat-vps1.onrender.com",
    "https://chat-vps2.onrender.com",
    "https://chat-vps3.onrender.com",
    "https://chat-vps4.onrender.com",
    "https://chat-vps5.onrender.com"
]

# Random chọn 1 server
url = random.choice(SERVERS)
sio = socketio.Client()

username = Prompt.ask("👤 Nhập tên của bạn")
console.clear()
console.print(Panel(f"[bold green]🔗 Đang kết nối tới {url}[/]", title="Chat Client"))

@sio.event
def connect():
    console.print(f"[bold green]✅ Đã kết nối tới server![/]")

@sio.event
def disconnect():
    console.print("[bold red]❌ Mất kết nối![/]")

@sio.on("message")
def on_message(data):
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(f"[cyan]{timestamp}[/] 💬 [bold yellow]{data}[/]")

try:
    sio.connect(url)
except Exception as e:
    console.print(f"[bold red]Không thể kết nối: {e}[/]")
    exit()

while True:
    try:
        msg = Prompt.ask(f"[bold blue]{username}[/]")
        if msg.strip() != "":
            sio.send(f"{username}: {msg}")
    except KeyboardInterrupt:
        console.print("\n[red]👋 Thoát chat[/]")
        sio.disconnect()
        break
