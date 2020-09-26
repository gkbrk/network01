import socket


class TCPPeer:
    def __init__(self, id, sock):
        self.id = id
        self.addr = addr
        self.send_buffer = b""
        self.recv_buffer = b""
        self.sock = sock

    def step(self):
        try:
            n = self.sock.send(self.send_buffer)
            self.send_buffer = self.send_buffer[n:]
        except:
            pass

        try:
            pass
        except:
            pass
