import hashlib
from pathlib import Path

class State:
    def __init__(self):
        self.challenge_index = 0
        self.flag_hash = b""
        self.workspace = ""

def simple_hash(state, secret_key: bytes) -> bytes:
    h = hashlib.sha256()
    h.update(secret_key)
    h.update(state.challenge_index.to_bytes(4, "little"))
    h.update(state.flag_hash)
    h.update(state.workspace.encode())
    return h.digest()

