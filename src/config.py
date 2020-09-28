import random

# Runtime config

settings = {}


def set(name, value):
    if isinstance(name, str):
        name = name.encode("ascii")

    if isinstance(value, str):
        value = value.encode("utf-8")
    settings[name] = value


def get(name, value=None):
    if isinstance(name, str):
        name = name.encode("ascii")
    val = settings.get(name, value)
    return val


def get_int(name, value=None):
    v = get(name)
    if not v:
        return value

    return int(v)


def get_bool(name, value=None):
    v = get(name)

    if v == b"true":
        return True
    if v == b"false":
        return False

    return value

set("addr", "127.0.0.1")
set("id", f"ANON{random.randint(99999, 9999999)}")
set("maxttl", "10")
set("temp_peer", "false")
set("tracer_interval", "5")
