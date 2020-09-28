import functools
import peers
import bencode
import config
import socket
import time
import random
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class TracerList:
    def __init__(self, N=64):
        self.N = N
        self.l = []

    def add_tracer(self, peer, node, ttl, latency):
        v = (peer, node, ttl, latency)
        self.l.append(v)

        while len(self.l) > self.N:
            self.l.pop(0)

    def select_peer(self, node):
        l = []

        for peer, n, ttl, latency in self.l:
            if node == n:
                l.append((peer, ttl, latency))

        if not l:
            return None
        return min(l, key=lambda x: x[2])[0]


tracerList = TracerList()


def handle(message, peer):
    peer.received += 1

    if message[b"to"] == config.get("id") and message[b"type"] == b"data":
        handle_self(message, peer)

    if message[b"type"] == b"tracer":
        handle_tracer(message, peer)

    if message[b"type"] == b"data":
        handle_data(message, peer)

    if message[b"type"] == b"dbg.tracert":
        handle_traceroute(message, peer)


def handle_self(message, peer):
    fr = message[b"from"]
    print("------")
    print(f"Received message from {fr}, routed by {peer.alias}")
    print(message[b"data"])
    print("------")


def handle_tracer(message, peer):
    ts = message[b"ts"]

    latency = seconds_ns() - ts
    tracerList.add_tracer(peer, message[b"from"], message[b"ttl"], latency)

    if len(peers.peers) == 1:
        return
    if message[b"ttl"] > config.get_int("maxttl"):
        return

    np = peer
    while np == peer:
        np = random.choice(peers.peers)
    message[b"ttl"] += 1
    np.sent += 1
    sock.sendto(bencode.encode(message), np.addr)


def handle_data(message, peer):
    if message[b"to"] == config.get("id"):
        return

    if message[b"ttl"] > config.get_int("maxttl"):
        return

    np = tracerList.select_peer(message[b"to"])

    if np:
        message[b"ttl"] += 1
        np.sent += 1
        sock.sendto(bencode.encode(message), np.addr)


def handle_traceroute(message, peer):
    if message[b"to"] == config.get("id"):
        send_data(message[b"from"], message[b"rt"])
        return

    if message[b"ttl"] > config.get_int("maxttl"):
        return

    np = tracerList.select_peer(message[b"to"])

    if np:
        message[b"ttl"] += 1
        message[b"rt"] += b"," + config.get("id")
        np.sent += 1
        sock.sendto(bencode.encode(message), np.addr)


def send_data(node, data):
    node = node
    np = tracerList.select_peer(node)

    addr = random.choice(peers.peers).addr

    if np:
        addr = np.addr

    msg = {
        "type": "data",
        "from": config.get("id"),
        "to": node,
        "data": data,
        "ttl": 0,
    }
    sock.sendto(bencode.encode(msg), addr)

def send_tracert(node):
    node = node
    np = tracerList.select_peer(node)

    addr = random.choice(peers.peers).addr

    if np:
        addr = np.addr

    msg = {
        "type": "dbg.tracert",
        "from": config.get("id"),
        "rt": config.get("id"),
        "to": node,
        "ttl": 0,
    }
    sock.sendto(bencode.encode(msg), addr)


def seconds_ns(sec=60):
    return int((time.time() * 1000) % (sec * 1000))


def tracer_task():
    while True:
        while len(peers.peers) < 1:
            time.sleep(5)

        peer = random.choice(peers.peers)
        peer.sent += 1

        msg = {
            "type": "tracer",
            "from": config.get("id"),
            "to": "SYSTEM",
            "ttl": 0,
            "ts": seconds_ns(),
        }
        sock.sendto(bencode.encode(msg), peer.addr)
        time.sleep(config.get_int("tracer_interval"))


def listener():
    addr = config.get("addr")
    port = config.get_int("port", 0)

    sock.bind((addr, port))

    while True:
        try:
            # Clean temporary peers
            peers.clean_temp()

            packet, peer_addr = sock.recvfrom(2048)
            peer = peers.find_by_addr(peer_addr)

            if not peer:
                if config.get_bool("temp_peer"):
                    peer = peers.create_temp(peer_addr)
                else:
                    continue

            message = bencode.decode(packet)
            handle(message, peer)
            peer.last_received = time.time()
        except Exception as e:
            import traceback
            traceback.print_tb(sys.exc_info()[2])
