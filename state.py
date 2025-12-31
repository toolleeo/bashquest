import hashlib
from pathlib import Path

class State:
    def __init__(self):
        self.challenge_index = 0
        self.flag_hash = b""
        self.workspace = ""
        self.passed_challenges: set[str] = set()  # store IDs of passed challenges

