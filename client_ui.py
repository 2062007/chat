import socketio, random, requests
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

# ---- Load history khi vừa connect ----
def load_history():
    try:
        r = requests.get(f"{url}/history", timeout=5)
        if r.status_code == 200:
            messages = r.json()
            console.print(Panel("[bold cyan]📜 50 tin nhắn gần nhất[/]"))
            for item in messages:
                console.print(f"[cyan]{item['time']}[/] 💬 [yellow]{item['msg']}[/]")
        else:
            console.print(f"[red]⚠️ Không lấy được history (HTTP {r.status_code})[/]")
    except Exception as e:
        console.print(f"[red]⚠️ Lỗi load history: {e}[/]")

@sio.event
def connect():
    console.print(f"[bold green]✅ Đã kết nối tới server![/]")
    load_history()  # load history khi connect

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
