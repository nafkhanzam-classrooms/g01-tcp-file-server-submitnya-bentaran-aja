import socket
import select
import os

HOST = "127.0.0.1"
PORT = 12344
FOLDER = "server_files"

os.makedirs(FOLDER, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.bind((HOST, PORT))
server.listen()

poller = select.poll()
poller.register(server, select.POLLIN)

clients = {}
buffer = {}   # text buffer per client
upload_state = {}  # upload state per client

def send_line(conn, msg):
    conn.sendall((msg + "\n").encode())

def disconnect(fd):
    conn = clients.get(fd)
    if conn:
        poller.unregister(fd)
        conn.close()

    clients.pop(fd, None)
    buffer.pop(fd, None)
    upload_state.pop(fd, None)


print("[SERVER] running on Linux…")


while True:
    events = poller.poll(1000)

    for fd, event in events:

        # ---------------------------------------------
        # NEW CONNECTION
        # ---------------------------------------------
        if fd == server.fileno():
            conn, addr = server.accept()
            conn.setblocking(False)

            clients[conn.fileno()] = conn
            buffer[conn.fileno()] = ""
            poller.register(conn, select.POLLIN)

            print("[CONNECT]", addr)
            continue

        conn = clients.get(fd)
        if conn is None:
            continue

        # ---------------------------------------------
        # UPLOAD MODE (binary)
        # ---------------------------------------------
        if fd in upload_state:
            st = upload_state[fd]

            # First read EXACTLY 16 bytes (filesize)
            if st["expect_size"]:
                need = 16 - len(st["sizebuf"])
                chunk = conn.recv(need)

                if not chunk:
                    continue

                st["sizebuf"] += chunk
                if len(st["sizebuf"]) < 16:
                    continue

                st["size"] = int(st["sizebuf"].decode().strip())
                st["expect_size"] = False
                st["data"] = b""
                continue

            # Now receive binary file data
            chunk = conn.recv(4096)
            if not chunk:
                continue  # DO NOT disconnect

            st["data"] += chunk

            # finish?
            if len(st["data"]) >= st["size"]:
                path = os.path.join(FOLDER, st["filename"])
                with open(path, "wb") as f:
                    f.write(st["data"])

                print("[UPLOAD] saved", st["filename"])
                send_line(conn, "UPLOAD_DONE")
                upload_state.pop(fd)
            continue

        # ---------------------------------------------
        # NORMAL COMMAND MODE (text)
        # ---------------------------------------------
        chunk = conn.recv(4096)
        if chunk == b"":
            print("[DISCONNECT]")
            disconnect(fd)
            continue

        try:
            buffer[fd] += chunk.decode()
        except:
            continue  # skip broken decode

        # Process full commands
        while "\r\n" in buffer or "\n" in buffer[fd]:
            line, buffer[fd] = buffer[fd].split("\n", 1)

            # /list
            if line == "/list":
                files = ",".join(os.listdir(FOLDER))
                send_line(conn, "LIST|" + files)
                continue

            # /upload filename
            if line.startswith("/upload "):
                filename = line.split()[1]
                send_line(conn, "UPLOAD_OK")

                upload_state[fd] = {
                    "filename": filename,
                    "expect_size": True,
                    "sizebuf": b""
                }
                continue

            # /download filename
            if line.startswith("/download "):
                filename = line.split()[1]
                path = os.path.join(FOLDER, filename)

                if not os.path.exists(path):
                    send_line(conn, "ERROR|File not found")
                    continue

                size = os.path.getsize(path)
                send_line(conn, f"DOWNLOAD_BEGIN|{filename}|{size}")

                with open(path, "rb") as f:
                    conn.sendall(f.read())

                send_line(conn, "DOWNLOAD_DONE")
                print("[DOWNLOAD] sent:", filename)
                continue

            # fallback: broadcast
            msg = "BROADCAST|" + line
            for fd2, c2 in clients.items():
                if fd2 != fd:
                    send_line(c2, msg)
