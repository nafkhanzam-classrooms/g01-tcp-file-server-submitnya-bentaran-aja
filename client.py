import socket
import threading
import os
import queue
import base64

HOST = "127.0.0.1"
PORT = 12345
UPLOAD_DIR = "client_files"

os.makedirs(UPLOAD_DIR, exist_ok=True)

upload_q = queue.Queue()
download_q = queue.Queue()


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print("Connected!")
print("Use '/list' to see all files")
print("Use '/upload [filename]' to upload a file")
print("Use '/download [filename]' to get a file")

def listener():
    buffer = ""
    while True:
        try:
            chunk = client.recv(4096).decode()
            if not chunk:
                break

            buffer += chunk

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                process_line(line)

        except:
            break


def process_line(line):
    if line.startswith("BROADCAST|"):
        print("\n[CHAT]", line.split("|", 1)[1])

    elif line == "UPLOAD_OK":
        upload_q.put("OK")

    elif line == "UPLOAD_DONE":
        upload_q.put("DONE")

    elif line.startswith("LIST|"):
        print("\n[FILES]", line[5:])

    elif line.startswith("ERROR|"):
        print("\n[ERROR]", line[6:])

    elif line.startswith("DOWNLOAD_BEGIN|"):
        _, name, size = line.split("|")
        download_q.put((name, int(size)))

    elif line == "DOWNLOAD_DONE":
        download_q.put("DONE")


threading.Thread(target=listener, daemon=True).start()

while True:
    cmd = input(">> ")

    if not cmd.startswith("/"):
        client.sendall((cmd + "\n").encode())
        continue

    if cmd == "/list":
        client.sendall(b"/list\n")
        continue

    if cmd.startswith("/upload"):
        client.sendall((cmd + "\n").encode())
        filename = cmd.split()[1]
        path = os.path.join(UPLOAD_DIR, filename)

        if upload_q.get() != "OK":
            print("Upload failed!")
            continue

        try:
            with open(path, "rb") as f:
                data = f.read()
        except:
            data = b""

        client.sendall(str(len(data)).ljust(16).encode())

        client.sendall(data)

        upload_q.get()
        print("[UPLOAD] Done.")
        continue

    if cmd.startswith("/download"):
        client.sendall((cmd + "\n").encode())
        name, size = download_q.get()

        raw = b""
        while len(raw) < size:
            raw += client.recv(4096)

        download_q.get()

        with open(os.path.join(UPLOAD_DIR, name), "wb") as f:
            f.write(raw)

        print("[DOWNLOAD] Saved", name)
        continue

    # Unknown command
    client.sendall((cmd + "\n").encode())