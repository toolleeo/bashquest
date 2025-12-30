#!/usr/bin/env python3

import os
import sys
import stat
import shutil
import random
import time
import pickle
import hashlib
from pathlib import Path

# ===================== CONFIG =====================

SECRET_KEY = b"bashquest_internal_secret"
CONFIG_DIR = Path.home() / ".config" / "bashquest"

# ===================== STATE =====================

class State:
    def __init__(self):
        self.challenge = 1
        self.flag_hash = b""
        self.workspace = ""

def simple_hash(state: State) -> bytes:
    h = hashlib.sha256()
    h.update(SECRET_KEY)
    h.update(state.challenge.to_bytes(4, "little"))
    h.update(state.flag_hash)
    h.update(state.workspace.encode())
    return h.digest()

def state_dir() -> Path:
    return CONFIG_DIR

def load_state() -> State | None:
    try:
        with open(state_dir() / "state.bin", "rb") as f:
            state, checksum = pickle.load(f)
        if checksum != simple_hash(state):
            return None
        return state
    except Exception:
        return None

def save_state(state: State):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    checksum = simple_hash(state)
    with open(CONFIG_DIR / "state.bin", "wb") as f:
        pickle.dump((state, checksum), f)

# ===================== UTIL =====================

def make_writable_recursive(path: Path):
    if not path.exists():
        return
    try:
        path.chmod(0o777)
    except Exception:
        pass
    if path.is_dir():
        for p in path.iterdir():
            make_writable_recursive(p)

def reset_workspace(ws: Path):
    if ws.exists():
        make_writable_recursive(ws)
        shutil.rmtree(ws)
    ws.mkdir(parents=True, exist_ok=True)

def mkdir(p: Path):
    p.mkdir()

# ===================== RANDOM HELPERS =====================

short_names = [
    "bin","lib","src","tmp","var",
    "log","opt","dev","etc","run"
]

long_names = [
    "extraordinarily_long_directory_name",
    "another_unnecessarily_verbose_directory",
    "final_directory_that_you_should_autocomplete",
    "ridiculously_specific_and_annoying_directory_name",
    "this_directory_name_is_way_too_long"
]

def random_from(v):
    return random.choice(v)

def hash_flag(s: str) -> bytes:
    return hashlib.sha256(s.encode()).digest()

# ===================== CHALLENGE 1 =====================

def setup_challenge_1(state: State):
    ws = Path("workspace").resolve()
    reset_workspace(ws)

    d1 = random_from(short_names)
    d2 = random_from(short_names)
    d3 = random_from(short_names)

    mkdir(ws / d1)
    mkdir(ws / d1 / d2)
    mkdir(ws / d1 / d2 / d3)

    state.challenge = 1
    state.flag_hash = hash_flag(d3)
    state.workspace = str(ws)
    save_state(state)

    print("Challenge 1:")
    print("Three directories were created, one inside another.")
    print("Find the deepest one. The flag is its name.")

def check_challenge_1(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash

# ===================== CHALLENGE 2 =====================

def setup_challenge_2(state: State):
    ws = Path(state.workspace)
    reset_workspace(ws)

    d1, d2, d3 = long_names[:3]

    mkdir(ws / d1)
    mkdir(ws / d1 / d2)
    mkdir(ws / d1 / d2 / d3)

    state.challenge = 2
    state.flag_hash = hash_flag(d3)
    save_state(state)

    print("Challenge 2:")
    print("Same task, but directory names are painful to type.")
    print("Use tab completion.")

def check_challenge_2(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash

# ===================== CHALLENGE 3 =====================

def setup_challenge_3(state: State):
    ws = Path("workspace").resolve()
    reset_workspace(ws)

    start = ws / "start"
    mkdir(start)

    go_left = start / "go_left"
    go_right = start / "go_right"
    mkdir(go_left)
    mkdir(go_right)

    treasure = go_left / "treasure"
    deadend = go_right / "deadend"
    mkdir(treasure)
    mkdir(deadend)

    state.challenge = 3
    state.flag_hash = hash_flag("treasure")
    state.workspace = str(ws)
    save_state(state)

    print("Challenge 3 (CD mastery):")
    print("Navigate the directory maze using 'cd'.")
    print("Only step-by-step navigation works.")

def check_challenge_3(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash

# ===================== CHALLENGE 4 =====================

def random_dirname(length=6):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.choice(chars) for _ in range(length))

def setup_challenge_4(state: State):
    ws = Path("workspace").resolve()
    reset_workspace(ws)

    d1 = random_dirname()
    d2 = random_dirname()
    d3 = random_dirname()

    p1 = ws / d1
    p2 = p1 / d2
    p3 = p2 / d3

    mkdir(p1)
    mkdir(p2)
    mkdir(p3)

    (p1 / "INSTRUCTIONS.txt").write_text(f"To continue, cd into:\n{d2}\n")
    (p2 / "INSTRUCTIONS.txt").write_text(f"To continue, cd into:\n{d3}\n")
    (p3 / "INSTRUCTIONS.txt").write_text(
        "You reached the deepest directory.\n"
        "The directory name is the flag.\n"
        "Use pwd to show the full path.\n"
    )

    x = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    r = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH

    for p in (p1, p2, p3):
        p.chmod(x)

    for f in (p1/"INSTRUCTIONS.txt", p2/"INSTRUCTIONS.txt", p3/"INSTRUCTIONS.txt"):
        f.chmod(r)

    state.challenge = 4
    state.flag_hash = hash_flag(d3)
    state.workspace = str(ws)
    save_state(state)

    print("Challenge 4 (permissions + cd):")
    print("You cannot list directories.")
    print("Read INSTRUCTIONS.txt and use 'cd'.")
    print("The flag is the deepest directory name.")
    print("Use pwd anytime.")

def check_challenge_4(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash

# ===================== MAIN =====================

def main():
    random.seed(time.time())

    if len(sys.argv) < 2:
        print("Usage: bashquest start | submit FLAG | reset")
        return

    cmd = sys.argv[1]
    state = load_state()

    if not state:
        state = State()
        save_state(state)

    if cmd == "reset":
        make_writable_recursive(state_dir())
        make_writable_recursive(Path("workspace"))
        shutil.rmtree(state_dir(), ignore_errors=True)
        shutil.rmtree("workspace", ignore_errors=True)
        print("Progress reset.")
        return

    if cmd == "start":
        setup_challenge_1(state)
        return

    if cmd == "submit":
        if len(sys.argv) < 3:
            print("Missing flag.")
            return

        flag = sys.argv[2]

        checks = {
            1: check_challenge_1,
            2: check_challenge_2,
            3: check_challenge_3,
            4: check_challenge_4,
        }

        if state.challenge not in checks:
            print("All challenges completed.")
            return

        if not checks[state.challenge](state, flag):
            print("Wrong flag.")
            return

        print("Correct!")
        state.challenge += 1
        save_state(state)

        setups = {
            2: setup_challenge_2,
            3: setup_challenge_3,
            4: setup_challenge_4,
        }

        if state.challenge in setups:
            setups[state.challenge](state)
        else:
            print("You completed all challenges.")

        return

    print("Unknown command.")

if __name__ == "__main__":
    main()

