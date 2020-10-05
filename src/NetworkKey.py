import hmac
import bencode
import config

def sign(message):
    key = config.get("network-key")
    if b"sig" in message:
        del message[b"sig"]
    data = bencode.encode(message)
    sig = hmac.digest(key, data, "sha256")
    message[b"sig"] = sig
    return message

def check_signature(message):
    key = config.get("network-key")

    sig = message[b"sig"]
    del message[b"sig"]

    data = bencode.encode(message)
    message[b"sig"] = sig
    msig = hmac.digest(key, data, "sha256")

    return hmac.compare_digest(sig, msig)
