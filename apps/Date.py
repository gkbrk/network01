import client
import time

net = client.Client("DATE", ("127.0.0.1", 4455))

def got_packet(net, node, data):
    net.send(node, time.asctime())

net.on_packet = got_packet
net.run()
