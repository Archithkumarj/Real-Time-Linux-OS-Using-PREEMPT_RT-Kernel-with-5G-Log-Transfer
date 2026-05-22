from flask import Flask
from flask_socketio import SocketIO
import socket

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

UDP_PORT = 9000


# ── Web UI ─────────────────────────────────────────────
@app.route("/")
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
<title>Live Log Monitor</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.1/socket.io.min.js"></script>

<style>
body {
    margin:0;
    background:#0b0f14;
    font-family: monospace;
    color:#e0e0e0;
}

header {
    background:#111827;
    padding:15px;
    font-size:18px;
    color:#00ff9c;
    border-bottom:1px solid #222;
}

#controls {
    padding:10px;
    background:#0f172a;
    border-bottom:1px solid #222;
}

button {
    background:#1f2937;
    color:white;
    border:none;
    padding:6px 12px;
    margin-right:10px;
    cursor:pointer;
    border-radius:5px;
}

button:hover {
    background:#374151;
}

#logBox {
    height:85vh;
    overflow:auto;
    padding:10px;
}

.entry {
    padding:4px 0;
    border-bottom:1px solid #111;
}

.ts { color:#888; margin-right:10px; }
.src { color:#00bcd4; margin-right:10px; }

.info { color:#9cdcfe; }
.warn { color:#ffd740; }
.error { color:#ff5252; font-weight:bold; }
</style>
</head>

<body>

<header>● LIVE LOG MONITOR</header>

<div id="controls">
    <button onclick="clearLogs()">Clear</button>
    <button onclick="toggleScroll()">Auto Scroll: ON</button>
</div>

<div id="logBox"></div>

<script>
const socket = io();
let autoScroll = true;

function clearLogs() {
    document.getElementById("logBox").innerHTML = "";
}

function toggleScroll() {
    autoScroll = !autoScroll;
    event.target.innerText = "Auto Scroll: " + (autoScroll ? "ON" : "OFF");
}

socket.on("log", (data) => {
    const box = document.getElementById("logBox");
    const div = document.createElement("div");

    const now = new Date().toLocaleTimeString();
    let msg = data.message || "";

    let cls = "info";
    if (/error|fail/i.test(msg)) cls = "error";
    else if (/warn/i.test(msg)) cls = "warn";

    div.className = "entry";
    div.innerHTML = `
        <span class="ts">${now}</span>
        <span class="src">${data.source}</span>
        <span class="${cls}">${msg}</span>
    `;

    box.appendChild(div);

    if (autoScroll) {
        box.scrollTop = box.scrollHeight;
    }
});
</script>

</body>
</html>
'''


# ── UDP Receiver ───────────────────────────────────────
def udp_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))

    print(f"[UDP] Listening on port {UDP_PORT}")

    while True:
        data, addr = sock.recvfrom(65535)

        message = data.decode("utf-8", errors="replace").strip()
        if message:
            print(f"[{addr[0]}] {message}")

            socketio.emit("log", {
                "source": addr[0],
                "message": message
            })


# ── Main ───────────────────────────────────────────────
if __name__ == "__main__":
    socketio.start_background_task(udp_receiver)

    print("🌐 Open: http://localhost:5000")

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True
    )
