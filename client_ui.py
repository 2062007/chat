import requests
from datetime import datetime
import socketio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align

console = Console()

# ==== Danh sách 5 VPS ====
SERVERS = [
    "https://chat-vps1.onrender.com",
    "https://chat-vps2.onrender.com",
    "https://chat-vps3.onrender.com",
    "https://chat-vps4.onrender.com",
    "https://chat-vps5.onrender.com"
]

COLORS = ["cyan", "magenta", "green", "yellow", "blue", "red"]
user_colors = {}

def get_color(user: str):
    if user not in user_colors:
        user_colors[user] = COLORS[len(user_colors) % len(COLORS)]
    return user_colors[user]

def show_message(user, msg, ts=None, me=False):
    ts = ts or datetime.now().strftime("%H:%M:%S")
    color = get_color(user)

    header = f"[dim]{ts}[/] [bold {color}]{user}[/]"
    bubble = Panel(
        msg,
        title=header if not me else None,
        subtitle=header if me else None,
        subtitle_align="right" if me else "left",
        border_style=color,
        expand=False,
        padding=(0, 2),
        highlight=True,
    )

    if me:
        console.print(Align.right(bubble))
    else:
        console.print(Align.left(bubble))

def load_history(base_url, username):
    try:
        r = requests.get(f"{base_url}/history?limit=15", timeout=6)
        if r.ok:
            msgs = r.json()
            if msgs:
                console.print(Panel(f"[bold cyan]📜 15 tin gần nhất từ {base_url}[/]", border_style="bright_black"))
                for it in msgs:
                    show_message(it["user"], it["msg"], it["time"], me=(it["user"] == username))
    except Exception as e:
        console.print(f"[red]⚠️ Lỗi load history {base_url}: {e}[/]")

def connect_server(base_url, username):
    sio = socketio.Client(reconnection=True, reconnection_attempts=0)

    @sio.event
    def connect():
        console.print(Panel(f"[green]✅ Kết nối {base_url}[/]", border_style="green"))
        load_history(base_url, username)

    @sio.event
    def disconnect():
        console.print(f"[red]❌ Mất kết nối {base_url}, thử reconnect...[/]")

    @sio.on("message")
    def on_message(data):
        try:
            show_message(data.get("user", "?"), data.get("msg", ""), data.get("time"), me=(data.get("user") == username))
        except Exception:
            console.print(f"[dim]{datetime.now().strftime('%H:%M:%S')}[/] 💬 {data}")

    try:
        sio.connect(base_url, transports=["websocket"], headers={"Origin": base_url})
    except Exception as e:
        console.print(f"[red]⚠️ Không connect {base_url}: {e}[/]")

    return sio

def main():
    username = Prompt.ask("👤 Nhập tên của bạn").strip() or "guest"
    clients = []

    # Kết nối tất cả server
    for url in SERVERS:
        sio = connect_server(url, username)
        clients.append(sio)

    console.print(Panel("[bold cyan]✨ Bắt đầu chat nào! Ctrl+C để thoát ✨[/]", border_style="cyan"))

    # Vòng lặp chat
    while True:
        try:
            text = Prompt.ask(f"[bold]{username}[/]").strip()
            if text:
                for sio in clients:
                    if sio.connected:
                        sio.send({"user": username, "msg": text})
                # In luôn tin nhắn của mình dạng bong bóng bên phải
                show_message(username, text, me=True)
        except KeyboardInterrupt:
            console.print("\n[red]👋 Thoát chat[/]")
            for sio in clients:
                try:
                    sio.disconnect()
                except:
                    pass
            break

if __name__ == "__main__":
    main()
