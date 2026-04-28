    #!/usr/bin/env python3
    import socket
    import threading
    import os

    HOST = "0.0.0.0"
    PORT = 5000
    CHAT_FILE = "chat.txt"


    def read_all() -> str:
        if not os.path.exists(CHAT_FILE):
            return ""
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return f.read()


    def append_line(line: str) -> None:
        with open(CHAT_FILE, "a", encoding="utf-8") as f:
            f.write(line.rstrip("
") + "
")


    def recv_all(conn: socket.socket) -> str:
        """Receive all data until the client closes the connection."""
        conn.settimeout(3.0)
        chunks = []
        while True:
            try:
                data = conn.recv(4096)
            except socket.timeout:
                break
            if not data:
                break
            chunks.append(data)
        return b"".join(chunks).decode("utf-8", errors="ignore")


    def handle_client(conn: socket.socket, addr):
        try:
            raw = recv_all(conn).strip("
")
            if not raw:
                return

            lines = raw.split("
", 1)
            cmd = lines[0].strip().upper()

            if cmd == "VIEW":
                content = read_all()
                conn.sendall(content.encode("utf-8"))

            elif cmd == "POST":
                msg = ""
                if len(lines) > 1:
                    msg = lines[1].strip()
                if msg:
                    append_line(msg)
                    conn.sendall(b"OK")
                else:
                    conn.sendall(b"ERROR: Empty message
")

            else:
                conn.sendall(b"ERROR: Unknown command. Use VIEW or POST.
")

        except Exception as e:
            try:
                conn.sendall(f"ERROR: {e}
".encode("utf-8", errors="ignore"))
            except Exception:
                pass
        finally:
            conn.close()


    def main():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(50)
        print(f"[SERVER] Running on {HOST}:{PORT} file={CHAT_FILE}")

        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


    if __name__ == "__main__":
        main()
