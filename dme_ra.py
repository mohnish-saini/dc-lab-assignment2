#!/usr/bin/env python3
import socket
import threading


class RicartAgrawalaDME:
    """
    Distributed mutual exclusion using Ricart–Agrawala algorithm.
    Fully distributed (no central lock server).
    Designed for 2 clients (Node-2 and Node-3).

    Message formats:
      REQUEST <ts> <sender>
      REPLY   <ts> <sender>
    """

    def __init__(self, self_id: str, listen_port: int, peer_id: str, peer_ip: str, peer_port: int):
        self.self_id = self_id
        self.listen_port = listen_port

        self.peer_id = peer_id
        self.peer_ip = peer_ip
        self.peer_port = peer_port

        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)

        self.clock = 0
        self.requesting = False
        self.in_cs = False
        self.my_req_ts = None

        self.reply_received = False
        self.deferred = False

        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _log(self, msg: str):
        print(f"[DME][{self.self_id}][clk={self.clock}] {msg}")

    def _send(self, msg: str):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        try:
            s.connect((self.peer_ip, self.peer_port))
            s.sendall(msg.encode("utf-8"))
        finally:
            s.close()

    def _listen_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", self.listen_port))
        s.listen(20)
        self._log(f"Listening on 0.0.0.0:{self.listen_port}")

        while True:
            conn, _ = s.accept()
            try:
                data = conn.recv(2048).decode("utf-8", errors="ignore").strip()
                if data:
                    self._handle_message(data)
            finally:
                conn.close()

    def _handle_message(self, data: str):
        parts = data.split()
        if len(parts) < 3:
            return

        mtype = parts[0].upper()
        ts = int(parts[1])
        sender = parts[2]

        with self.cv:
            # Lamport clock update
            self.clock = max(self.clock, ts) + 1

            if mtype == "REQUEST":
                self._log(f"RECV REQUEST from {sender} ts={ts}")

                # If not requesting and not in CS -> reply immediately
                if (not self.requesting) and (not self.in_cs):
                    self.clock += 1
                    self._send(f"REPLY {self.clock} {self.self_id}")
                    self._log(f"SEND REPLY to {sender} (free)")
                    return

                # Compare priority based on (timestamp, id)
                my_key = (self.my_req_ts, self.self_id)
                sender_key = (ts, sender)

                # If sender has higher priority and we are not in CS -> reply now
                if (not self.in_cs) and sender_key < my_key:
                    self.clock += 1
                    self._send(f"REPLY {self.clock} {self.self_id}")
                    self._log(f"SEND REPLY to {sender} (sender priority)")
                else:
                    self.deferred = True
                    self._log(f"DEFER reply to {sender}")

            elif mtype == "REPLY":
                self._log(f"RECV REPLY from {sender}")
                self.reply_received = True
                self.cv.notify_all()

    def acquire(self):
        """Request entry to critical section."""
        with self.cv:
            self.clock += 1
            self.requesting = True
            self.my_req_ts = self.clock
            self.reply_received = False

            self._log(f"SEND REQUEST ts={self.my_req_ts} to {self.peer_id}")
            self._send(f"REQUEST {self.my_req_ts} {self.self_id}")

            while not self.reply_received:
                self.cv.wait(timeout=1.0)

            self.requesting = False
            self.in_cs = True
            self._log("ENTER critical section")

    def release(self):
        """Release CS and send deferred reply if any."""
        with self.cv:
            self.in_cs = False
            self._log("EXIT critical section")

            if self.deferred:
                self.deferred = False
                self.clock += 1
                self._send(f"REPLY {self.clock} {self.self_id}")
                self._log(f"SEND deferred REPLY to {self.peer_id}")

            self.cv.notify_all()
