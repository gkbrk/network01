import struct
import socket
import sys
import functools
from collections import namedtuple

Debug = namedtuple("Debug", "method data")
Tracer = namedtuple("Tracer", "")
Data = namedtuple("Data", "srcport dstport data")

Message = namedtuple("Message", "fr to ttl inner")

PeerPacket = namedtuple("PeerPacket", "peer inner")


@functools.singledispatch
def encode(obj):
    raise Exception("Unknown type")


@encode.register(PeerPacket)
def _(msg):
    return msg.peer + encode(msg.inner)


@encode.register(Message)
def _(msg):
    buf = bytes()

    buf += msg.fr
    buf += msg.to

    buf += struct.pack("B", msg.ttl)

    buf += encode(msg.inner)

    return buf


@encode.register(Debug)
def _(msg):
    buf = bytes()

    buf += b"\xff"
    buf += msg.method.encode("ascii")
    buf += b"\x00"
    buf += msg.data.encode("ascii")

    return buf


@encode.register(Tracer)
def _(msg):
    return b"\x00"


@encode.register(Data)
def _(msg):
    buf = bytes()

    buf += struct.pack(">HH", msg.srcport, msg.dstport)
    buf += msg.data

    return buf
