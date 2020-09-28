import time
import random

peers = []


class Peer:
    def __init__(self, alias, addr):
        self.alias = alias
        self.addr = addr
        self.sent = 0
        self.received = 0
        self.last_received = time.time()
        self.is_temp = False


def find_by_addr(addr):
    for peer in peers:
        if peer.addr == addr:
            return peer


def clean_temp():
    for peer in list(peers):
        if peer.is_temp and time.time() - peer.last_received > 300:
            peers.remove(peer)


def create_temp(addr):
    n = f"TEMP{random.randint(99999, 9999999)}"
    p = Peer(n, addr)
    p.is_temp = True

    peers.append(p)
    return p
