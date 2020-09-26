import functools

# Bencode module
# ==============

# https://en.wikipedia.org/wiki/Bencode

# Encoding
# ========

# Implements the encode function to serialize Python values to byte arrays.


@functools.singledispatch
def encode(obj):
    raise Exception(f"Unknown type: {type(obj)}")


@encode.register(int)
def _(val):
    return b"i" + str(val).encode("ascii") + b"e"


@encode.register(str)
def _(val):
    return encode(val.encode("utf-8"))


@encode.register(bytes)
def _(val):
    return str(len(val)).encode("ascii") + b":" + val


@encode.register(list)
def _(val):
    r = b"l"
    for x in val:
        r += encode(x)
    r += b"e"

    return r


@encode.register(dict)
def _(val):
    r = b"d"

    for n in sorted(val.keys()):
        r += encode(n)
        r += encode(val[n])
    r += b"e"

    return r


# Decoding

import io


class Reader:
    def __init__(self, buf):
        self.buf = buf

    def getc(self):
        c = self.buf[0:1]
        self.buf = self.buf[1:]
        return c

    def peek(self):
        return self.buf[0:1]

    def read(self, n):
        buf, self.buf = self.buf[:n], self.buf[n:]
        return buf

    def read_until(self, pattern):
        buf = b""

        while not buf.endswith(pattern):
            buf += self.getc()

        return buf[: -len(pattern)]


def __read_int(r):
    """
    Read an integer from a Reader.
    """
    assert r.getc() == b"i"
    return int(r.read_until(b"e"))


def __read_str(r):
    l = int(r.read_until(b":"))
    return r.read(l)


def __read_list(r):
    assert r.getc() == b"l"

    l = []

    while not r.peek() == b"e":
        l.append(__read(r))

    r.getc()
    return l


def __read_dict(r):
    assert r.getc() == b"d"

    d = {}

    while not r.peek() == b"e":
        k = __read(r)
        v = __read(r)
        d[k] = v
    r.getc()
    return d


def __read(r):
    b = r.peek()

    if b == b"i":
        return __read_int(r)
    elif b == b"l":
        return __read_list(r)
    elif b == b"d":
        return __read_dict(r)
    else:
        return __read_str(r)


@functools.singledispatch
def decode(buf):
    raise Exception()


@decode.register(str)
def _(buf):
    return decode(buf.encode("utf-8"))


@decode.register(bytes)
def _(buf):
    r = Reader(buf)
    return __read(r)
