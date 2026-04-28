    #!/usr/bin/env python3
    import argparse
    import socket
    from datetime import datetime
    from dme_ra import RicartAgrawalaDME


    def server_send(server_ip: str, server_port: int, payload: str) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        try:
            s.connect((server_ip, server_port))
            s.sendall(payload.encode("utf-8"))

            data = b""
            while True:
                try:
                    chunk = s.recv(4096)
                except socket.timeout:
                    break
                if not chunk:
                    break
                data += chunk

            return data.decode("utf-8", errors="ignore")
        finally:
            s.close()


    def parse_args():
        p = argparse.ArgumentParser(description="Chat client with Distributed Mutual Exclusion")
        p.add_argument("--id", required=True, help="Client id/name (e.g., client1)")
        p.add_argument("--listen-port", type=int, required=True, help="DME listen port (e.g., 6002)")
        p.add_argument("--server-ip", required=True, help="Server PRIVATE IP")
        p.add_argument("--server-port", type=int, default=5000)
        p.add_argument("--peer-id", required=True, help="Other client id (e.g., client2)")
        p.add_argument("--peer-ip", required=True, help="Other client PRIVATE IP")
        p.add_argument("--peer-port", type=int, required=True, help="Other client DME port (e.g., 6003)")
        return p.parse_args()


    def main():
        args = parse_args()

        dme = RicartAgrawalaDME(
            self_id=args.id,
            listen_port=args.listen_port,
            peer_id=args.peer_id,
            peer_ip=args.peer_ip,
            peer_port=args.peer_port,
        )

        print(f"[APP][{args.id}] Ready.")
        print("Type commands INSIDE this prompt (NOT Linux terminal):")
        print("  view")
        print("  post <text>")
        print("  exit")

        while True:
            try:
                cmd = input("chat> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("
Exiting...")
                break

            if not cmd:
                continue

            if cmd == "exit":
                break

            if cmd == "view":
                out = server_send(args.server_ip, args.server_port, "VIEW
")
                print(out if out.strip() else "(no messages yet)")
                continue

            if cmd.startswith("post "):
                text = cmd[5:].strip()
                if not text:
                    print("Usage: post <text>")
                    continue

                dme.acquire()
                try:
                    ts = datetime.now().strftime("%d %b %I:%M%p")
                    line = f"{ts} {args.id}: {text}"
                    resp = server_send(args.server_ip, args.server_port, f"POST
{line}
")
                    if resp.strip() != "OK":
                        print("Server error:", resp)
                finally:
                    dme.release()
                continue

            print("Unknown command. Use: view | post <text> | exit")


    if __name__ == "__main__":
        main()
