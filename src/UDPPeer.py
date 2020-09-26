import packet
import socket


class UDPPeer:
    def __init__(self, name, addr):
        self.name = name
        self.last_seen = None
        self.addr = addr

    def send_message(self, message):
        encoded = packet.encode(message)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(encoded, self.addr)
