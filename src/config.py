import random

# Runtime config

settings = {}

settings[b"addr"] = "127.0.0.1"
settings[b"port"] = "4455"
settings[b"name"] = f"ANON{random.randint(99999, 9999999)}"
settings[b"maxttl"] = "10"


def set(name, value):
    if isinstance(name, str):
        name = name.encode("ascii")

    settings[name] = str(value)


def get(name, value=None):
    if isinstance(name, str):
        name = name.encode("ascii")
    return settings.get(name, value)


def get_int(name, value=None):
    v = get(name)
    if not v:
        return None

    return int(v)
