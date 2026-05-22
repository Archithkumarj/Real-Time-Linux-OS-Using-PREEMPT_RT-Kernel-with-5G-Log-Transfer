import socket
import subprocess

SERVER_IP = "192.168.1.39"   # <-- change to receiver IP
UDP_PORT  = 9000

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[SENDER] Streaming logs → {SERVER_IP}:{UDP_PORT}")

    process = subprocess.Popen(
        ["journalctl", "-f", "--no-pager", "--output=short"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    try:
        for line in process.stdout:
            line = line.strip()
            if line:
                sock.sendto(line.encode(), (SERVER_IP, UDP_PORT))
    except KeyboardInterrupt:
        print("\n[SENDER] Stopped")
    finally:
        process.terminate()
        sock.close()

if __name__ == "__main__":
    main()
