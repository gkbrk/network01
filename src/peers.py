peers = []


class Peer:
    def __init__(self, alias, addr):
        self.alias = alias
        self.addr = addr
        self.sent = 0
        self.received = 0
        self.last_received = None


def find_by_addr(addr):
    for peer in peers:
        if peer.addr == addr:
            return peer
