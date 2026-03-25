import socket
import os

HOST = '127.0.0.1'
PORT = 12345
FOLDER = "server_files"

os.makedirs(FOLDER, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Server (sync) running...")

def process_command(conn, addr, data):
    print(f"Received: {data}")

    if data == "/list":
        files = os.listdir(FOLDER)
        msg = "LIST|" + ",".join(files) + "\n"
        conn.sendall(msg.encode())

    elif data.startswith("/upload"):
        filename = data.split()[1]

        conn.sendall(b"UPLOAD_OK\n")

        size_data = conn.recv(16)
        filesize = int(size_data.decode().strip())

        received = 0
        raw = b""
        while received < filesize:
            chunk = conn.recv(4096)
            raw += chunk
            received += len(chunk)

        with open(f"{FOLDER}/{filename}", "wb") as f:
            f.write(raw)

        conn.sendall(b"UPLOAD_DONE\n")

    elif data.startswith("/download"):
        filename = data.split()[1]

        try:
            path = f"{FOLDER}/{filename}"
            size = os.path.getsize(path)

            conn.sendall(f"DOWNLOAD_BEGIN|{filename}|{size}\n".encode())

            with open(path, "rb") as f:
                conn.sendall(f.read())

            conn.sendall(b"DOWNLOAD_DONE\n")

        except:
            conn.sendall(b"ERROR|File not found\n")

    else:
        # not multi-client, so just send error
        conn.sendall(b"ERROR|Broadcast not supported in sync mode\n")


try:
    while True:
        conn, addr = server.accept()
        print(f"{addr} connected")

        buffer = ""

        while True:
            try:
                chunk = conn.recv(4096).decode()
                if not chunk:
                    break

                buffer += chunk

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    process_command(conn, addr, line)

            except:
                break

        conn.close()
        print(f"{addr} disconnected")

except KeyboardInterrupt:
    print("\n[SERVER] Shutting down...")
    server.close()