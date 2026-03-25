import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 12345
FOLDER = "server_files"

os.makedirs(FOLDER, exist_ok=True)

clients = []
lock = threading.Lock()


def send_line(conn, text):
    conn.sendall((text + "\n").encode())


def broadcast(message, sender=None):
    with lock:
        for c in clients:
            if c != sender:
                try:
                    send_line(c, f"BROADCAST|{message}")
                except:
                    clients.remove(c)


def handle_client(conn, addr):
    print(f"{addr} connected")

    with lock:
        clients.append(conn)

    buffer = ""

    while True:
        try:
            chunk = conn.recv(1024).decode()
            if not chunk:
                break

            buffer += chunk

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                process_command(conn, addr, line)

        except:
            break

    with lock:
        if conn in clients:
            clients.remove(conn)

    conn.close()
    print(f"{addr} disconnected")


def process_command(conn, addr, cmd):
    print(f"[SERVER] {addr}: {cmd}")

    if cmd == "/list":
        files = os.listdir(FOLDER)
        send_line(conn, "LIST|" + ",".join(files))

    elif cmd.startswith("/upload"):
        filename = cmd.split()[1]
        send_line(conn, "UPLOAD_OK")

        size = int(conn.recv(16).decode())
        received = 0
        data = b""

        while received < size:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            received += len(chunk)

        with open(f"{FOLDER}/{filename}", "wb") as f:
            f.write(data)

        send_line(conn, "UPLOAD_DONE")

    elif cmd.startswith("/download"):
        filename = cmd.split()[1]
        path = f"{FOLDER}/{filename}"

        if not os.path.exists(path):
            send_line(conn, "ERROR|File not found")
            return

        size = os.path.getsize(path)
        send_line(conn, f"DOWNLOAD_BEGIN|{filename}|{size}")

        with open(path, "rb") as f:
            conn.sendall(f.read())

        send_line(conn, "DOWNLOAD_DONE")

    else:
        broadcast(cmd, sender=conn)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server running...")

try:
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

except KeyboardInterrupt:
    server.close()
    print("\nServer stopped.")