import threading
import bencode
import socket
import time

class Client:
    def __init__(self, id, router):
        self.id = id
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.on_packet = None
        self.router = router

    def send(self, node, data):
        msg = {
            "from": self.id,
            "to": node,
            "ttl": 0,
            "type": "data",
            "data": data
        }
        self.s.sendto(bencode.encode(msg), self.router)

    def __thr(self):
        while True:
            msg = {
                "from": self.id,
                "to": "SYSTEM",
                "type": "tracer",
                "ttl": 0,
                "ts": int((time.time() * 1000) % (60 * 1000)),
            }
            self.s.sendto(bencode.encode(msg), self.router)
            time.sleep(5)

    def run(self):
        threading.Thread(target=self.__thr, daemon=True).start()

        while True:
            try:
                data, addr = self.s.recvfrom(2048)
                msg = bencode.decode(data)
                print(msg)

                if msg[b"to"] != self.id.encode("ascii"):
                    continue

                if msg[b"type"] == b"data" and self.on_packet is not None:
                    self.on_packet(self, msg[b"from"], msg[b"data"])

                if msg[b"type"] == b"dbg.tracert":
                    self.send(msg[b"from"], msg[b"rt"])
            except Exception:
                pass
