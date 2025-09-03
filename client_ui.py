import random, time, requests
from datetime import datetime
import socketio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

# ==== Danh sách 5 VPS của ông (đổi URL thực tế) ====
SERVERS = [
    "https://chat-vps1.onrender.com",
    "https://chat-vps2.onrender.com",
    "https://chat-vps3.onrender.com",
    "https://chat-vps4.onrender.com",
    "https://chat-vps5.onrender.com"
]

def pick_server(last=None):
    choices = [s for s in SERVERS if s != last] or SERVERS[:]
    return random.choice(choices)

def load_history(base_url):
    try:
        r = requests.get(f"{base_url}/history?limit=50", timeout=6)
        if r.ok:
            msgs = r.json()
            if msgs:
                console.print(Panel("[bold cyan]📜 50 tin nhắn gần nhất[/]"))
                for it in msgs:
                    console.print(f"[cyan]{it['time']}[/] 💬 [bold yellow]{it['user']}[/]: {it['msg']}")
    except Exception as e:
        console.print(f"[red]⚠️ Không load được history: {e}[/]")

def connect_with_failover(sio, username):
    tried = set()
    url = pick_server()
    while True:
        console.clear()
        console.print(Panel(f"[bold green]🔗 Đang kết nối tới {url}[/]", title="Chat Client"))
        try:
            # Ép WebSocket + gửi Origin để né 401 CORS
            sio.connect(url, transports=["websocket"], headers={"Origin": url})
            console.print("[bold green]✅ Đã kết nối tới server![/]")
            load_history(url)
            return url
        except Exception as e:
            console.print(f"[bold red]Không thể kết nối: {e}[/]")
            tried.add(url)
            if len(tried) >= len(SERVERS):
                console.print("[yellow]🌀 Thử lại từ đầu sau 2s...[/]")
                tried.clear()
                time.sleep(2)
            url = pick_server(last=url)

def main():
    sio = socketio.Client(reconnection=True, reconnection_attempts=0)  # auto reconnect vô hạn
    username = Prompt.ask("👤 Nhập tên của bạn").strip() or "guest"

    @sio.event
    def connect():
        # đã in ở connect_with_failover
        pass

    @sio.event
    def disconnect():
        console.print("[bold red]❌ Mất kết nối! Đang thử kết nối lại...[/]")

    @sio.on("message")
    def on_message(data):
        # data = {"user","msg","time"}
        try:
            ts = data.get("time") or datetime.now().strftime("%H:%M:%S")
            console.print(f"[cyan]{ts}[/] 💬 [bold yellow]{data.get('user','?')}[/]: {data.get('msg','')}")
        except Exception:
            console.print(f"[cyan]{datetime.now().strftime('%H:%M:%S')}[/] 💬 {data}")

    # Kết nối + failover
    connect_with_failover(sio, username)

    # Vòng lặp chat
    while True:
        try:
            text = Prompt.ask(f"[bold blue]{username}[/]").strip()
            if text:
                sio.send({"user": username, "msg": text})
        except KeyboardInterrupt:
            console.print("\n[red]👋 Thoát chat[/]")
            try:
                sio.disconnect()
            finally:
                break

if __name__ == "__main__":
    main()

