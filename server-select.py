import socket
import select
import os

HOST = '127.0.0.1'
PORT = 12345
FOLDER = "server_files"

os.makedirs(FOLDER, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

sockets = [server]
buffers = {}

print("Server (select) running...")


def process_command(sock, data):
    print(f"Received: {data}")

    if data == "/list":
        files = os.listdir(FOLDER)
        msg = "LIST|" + ",".join(files) + "\n"
        sock.sendall(msg.encode())

    elif data.startswith("/upload"):
        filename = data.split()[1]

        sock.sendall(b"UPLOAD_OK\n")

        size_data = sock.recv(16)
        filesize = int(size_data.decode().strip())

        received = 0
        raw = b""
        while received < filesize:
            chunk = sock.recv(4096)
            raw += chunk
            received += len(chunk)

        with open(f"{FOLDER}/{filename}", "wb") as f:
            f.write(raw)

        sock.sendall(b"UPLOAD_DONE\n")

    elif data.startswith("/download"):
        filename = data.split()[1]

        try:
            path = f"{FOLDER}/{filename}"
            size = os.path.getsize(path)

            sock.sendall(f"DOWNLOAD_BEGIN|{filename}|{size}\n".encode())

            with open(path, "rb") as f:
                sock.sendall(f.read())

            sock.sendall(b"DOWNLOAD_DONE\n")

        except:
            sock.sendall(b"ERROR|File not found\n")

    else:
        msg = f"BROADCAST|{data}\n"
        for s in sockets:
            if s != server and s != sock:
                try:
                    s.sendall(msg.encode())
                except:
                    s.close()
                    sockets.remove(s)


try:
    while True:
        read_sockets, _, _ = select.select(sockets, [], [])

        for sock in read_sockets:

            # new connection
            if sock == server:
                conn, addr = server.accept()
                print(f"{addr} connected")

                sockets.append(conn)
                buffers[conn] = ""

            # existing client
            else:
                try:
                    chunk = sock.recv(4096).decode()

                    if not chunk:
                        raise Exception()

                    buffers[sock] += chunk

                    while "\n" in buffers[sock]:
                        line, buffers[sock] = buffers[sock].split("\n", 1)
                        process_command(sock, line)

                except:
                    print("Client disconnected")
                    sock.close()
                    sockets.remove(sock)
                    buffers.pop(sock, None)

except KeyboardInterrupt:
    print("\n[SERVER] Shutting down...")
    server.close()