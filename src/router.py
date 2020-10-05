import functools
import peers
import bencode
import config
import socket
import time
import random
import sys
import NetworkKey

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class TracerList:
    def __init__(self, N=2048):
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
            if not peer in peers.peers:
                continue

            if node == n:
                l.append((peer, ttl, latency))

        if not l:
            return random.choice(peers.peers)
        return min(l[::-1], key=lambda x: (x[1], x[2]))[0]


tracerList = TracerList()


def handle(message, peer):
    peer.received += 1

    if message[b"to"] == config.get("id"):
        handle_self(message, peer)
        return

    if message[b"type"] == b"tracer":
        handle_tracer(message, peer)

    if message[b"type"] == b"dbg.tracert":
        message[b"rt"] += b"," + config.get("id")

    if message[b"to"] == b"SYSTEM":
        return route_random(message, peer)

    route_message(message, peer)

def handle_self(message, peer):
    if message[b"type"] == b"data":
        handle_self_data(message, peer)
    elif message[b"type"] == b"dbg.selfupdate":
        import selfUpdate
        selfUpdate.update()
    elif message[b"type"] == b"dbg.tracert":
        send_data(message[b"from"], b"Traceroute result: " + message[b"rt"])

import os
audioTarget = None
dsp = None

def handle_self_data(message, peer):
    if dsp:
        os.write(dsp, message[b"data"])
        return

    fr = message[b"from"]
    print("------")
    print(f"Received message from {fr}, routed by {peer.alias}")
    print(message[b"data"])
    print("------")


def handle_tracer(message, peer):
    ts = message[b"ts"]

    latency = seconds_ns() - ts
    tracerList.add_tracer(peer, message[b"from"], message[b"ttl"], latency)

def route_random(message, peer):
    if len(peers.peers) < 2:
        return

    if message[b"ttl"] > config.get_int("maxttl"):
        return

    np = peer

    while np == peer:
        np = random.choice(peers.peers)

    message[b"ttl"] += 1

    np.send_packet(message)

def route_message(message, peer):
    if message[b"ttl"] > config.get_int("maxttl"):
        return

    np = tracerList.select_peer(message[b"to"])

    if np:
        message[b"ttl"] += 1
        np.sent += 1
        np.send_packet(message)

def send_packet(node, **kwargs):
    msg = {
        "to": bencode.utf(node),
        "from": config.get("id"),
        "type": "data",
        "ttl": 0,
    }

    for key in kwargs:
        msg[key] = kwargs[key]

    np = tracerList.select_peer(node)
    np.send_packet(msg)


def send_data(node, data):
    send_packet(node, type="data", data=data)

def send_update(node):
    send_packet(node, type="dbg.selfupdate")

def send_tracert(node):
    send_packet(node, type="dbg.tracert", rt=config.get("id"))


def seconds_ns(sec=60):
    return int((time.time() * 1000) % (sec * 1000))

def audio_task():
    while True:
        if dsp:
            buf = os.read(dsp, 1400)
            send_data(audioTarget, buf)

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
        peer.send_packet(msg)
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
            message = bencode.decode(packet)

            if config.get_bool("dumpraw"):
                print(packet)


            key = config.get("network-key")

            if key:
                assert NetworkKey.check_signature(message)

            peer = peers.find_by_addr(peer_addr)

            if not peer:
                if config.get_bool("temp_peer"):
                    peer = peers.create_temp(peer_addr)
                else:
                    continue


            if config.get_bool("dump"):
                print(message)
            #print(message, peer_addr, peer.alias)
            handle(message, peer)
            peer.last_received = time.time()
        except Exception as e:
            pass
            #import traceback
            #traceback.print_tb(sys.exc_info()[2])
