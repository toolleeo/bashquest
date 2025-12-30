#!/usr/bin/env python3

import argparse
import stat
import shutil
import random
import time
import pickle
import hashlib
from pathlib import Path

# ===================== CONFIG =====================

CONFIG_DIR = Path.home() / ".config" / "bashquest"
WORKSPACE_DIR = "workspace"
INSTRUCTIONS = "INSTRUCTIONS.txt"

def load_secret_key() -> bytes:
    env_file = CONFIG_DIR / "env"
    if not env_file.exists():
        print("Fatal error: secret env file not found.")
        sys.exit(1)

    with env_file.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                if key == "SECRET_KEY":
                    return value.encode()

    print("Fatal error: SECRET_KEY not found in env file.")
    sys.exit(1)


SECRET_KEY = load_secret_key()

# ===================== ARGPARSE =====================

def init_argparser():
    parser = argparse.ArgumentParser(description="Shell quest (CTF-style)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("start", help="start or restart the quest")
    sub.add_parser("list", help="list all challenges")
    sub.add_parser("current", help="show current challenge")
    goto = sub.add_parser("goto", help="jump to a specific challenge (resets workspace)")
    goto.add_argument(
        "target",
        help="challenge number (1-based) or challenge id"
    )
    submit = sub.add_parser("submit", help="submit a flag")
    submit.add_argument(
        "flag",
        help="string to submit"
    )
    sub.add_parser("done", help="cancel the quest and cleanup")

    return parser

# ===================== STATE =====================

class State:
    def __init__(self):
        self.challenge_index = 0
        self.flag_hash = b""
        self.workspace = ""

def simple_hash(state: State) -> bytes:
    h = hashlib.sha256()
    h.update(SECRET_KEY)
    h.update(state.challenge_index.to_bytes(4, "little"))
    h.update(state.flag_hash)
    h.update(state.workspace.encode())
    return h.digest()

def load_state():
    try:
        with open(CONFIG_DIR / "state.bin", "rb") as f:
            state, checksum = pickle.load(f)
        return state if checksum == simple_hash(state) else None
    except Exception:
        return None

def save_state(state: State):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_DIR / "state.bin", "wb") as f:
        pickle.dump((state, simple_hash(state)), f)

# ===================== UTIL =====================

def make_writable_recursive(p: Path):
    if not p.exists():
        return
    try:
        p.chmod(0o777)
    except Exception:
        pass
    if p.is_dir():
        for c in p.iterdir():
            make_writable_recursive(c)

def reset_workspace(ws: Path):
    if ws.exists():
        make_writable_recursive(ws)
        shutil.rmtree(ws)
    ws.mkdir(parents=True, exist_ok=True)

def hash_flag(s: str) -> bytes:
    return hashlib.sha256(s.encode()).digest()

def resolve_challenge_index(target: str) -> int | None:
    # numeric (1-based)
    if target.isdigit():
        idx = int(target) - 1
        if 0 <= idx < len(CHALLENGES):
            return idx
        return None

    # by id
    for i, c in enumerate(CHALLENGES):
        if c["id"] == target:
            return i

    return None

# ===================== HELPERS =====================

short_names = ["bin","lib","src","tmp","var","log","opt","dev","etc","run"]

def random_dirname(n=6):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.choice(chars) for _ in range(n))

# ===================== Challenge implementations =====================

# ===================== Challenge: cat a file =====================

def setup_cat_file(state: State):
    ws = Path(WORKSPACE_DIR).resolve()
    reset_workspace(ws)

    possible_flags = [
        "hello",
        "banana",
        "penguin",
        "ocean",
        "terminal",
        "kernel",
    ]

    flag = random.choice(possible_flags)

    file_path = ws / "message.txt"
    file_path.write_text(
        "The flag is the word below:\n"
        f"{flag}\n"
    )

    state.flag_hash = hash_flag(flag)
    state.workspace = str(ws)


def check_cat_file(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash


def setup_find_deepest_directory(state: State):
    ws = Path(WORKSPACE_DIR).resolve()
    reset_workspace(ws)

    d1, d2, d3 = random.sample(short_names, 3)
    (ws / d1 / d2 / d3).mkdir(parents=True)

    state.flag_hash = hash_flag(d3)
    state.workspace = str(ws)

def check_find_deepest_directory(state, flag):
    return hash_flag(flag) == state.flag_hash


# ===================== TAB COMPLETION (AMBIGUOUS + BRANCHING) =====================

def random_ambiguous_name(length=20):
    chars = ["0", "O", "1", "l"]
    return "".join(random.choice(chars) for _ in range(length))


def setup_tab_completion_puzzle(state: State):
    ws = Path(WORKSPACE_DIR).resolve()
    reset_workspace(ws)

    # Ambiguous directory names
    d1_main = random_ambiguous_name()
    d1_fake = random_ambiguous_name()

    d2_main = random_ambiguous_name()
    d2_fake = random_ambiguous_name()

    d3 = random_ambiguous_name()
    d4 = random.choice(short_names)  # deepest directory (flag)

    # Level 1
    p1_main = ws / d1_main
    p1_fake = ws / d1_fake
    p1_main.mkdir()
    p1_fake.mkdir()

    # Level 2 (only under main path)
    p2_main = p1_main / d2_main
    p2_fake = p1_main / d2_fake
    p2_main.mkdir()
    p2_fake.mkdir()

    # Level 3
    p3 = p2_main / d3
    p3.mkdir()

    # Level 4 (flag)
    p4 = p3 / d4
    p4.mkdir()

    state.flag_hash = hash_flag(d4)
    state.workspace = str(ws)
    save_state(state)


def check_tab_completion_puzzle(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash


def check_cd_maze(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash

def setup_cd_maze(state: State):
    ws = Path(WORKSPACE_DIR).resolve()
    reset_workspace(ws)

    start = ws / "start"
    go_left = start / "go_left"
    go_right = start / "go_right"
    treasure = go_left / "treasure"
    deadend = go_right / "deadend"

    treasure.mkdir(parents=True)
    deadend.mkdir(parents=True)

    state.flag_hash = hash_flag("treasure")
    state.workspace = str(ws)

def setup_cd_permissions_puzzle(state: State):
    ws = Path(WORKSPACE_DIR).resolve()
    reset_workspace(ws)

    d1, d2, d3 = random_dirname(), random_dirname(), random_dirname()
    p1, p2, p3 = ws / d1, ws / d1 / d2, ws / d1 / d2 / d3
    p3.mkdir(parents=True)

    (p1 / instructions).write_text(f"To continue, cd into:\n{d2}\n")
    (p2 / instructions).write_text(f"To continue, cd into:\n{d3}\n")
    (p3 / instructions).write_text(
        "You reached the deepest directory.\n"
        "The directory name is the flag.\n"
        "Use pwd to show the full path.\n"
    )

    x = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    r = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH

    for p in (p1, p2, p3):
        p.chmod(x)
    for f in (p1/INSTRUCTIONS, p2/INSTRUCTIONS, p3/INSTRUCTIONS):
        f.chmod(r)

    state.flag_hash = hash_flag(d3)
    state.workspace = str(ws)

def check_cd_permissions_puzzle(state, flag):
    return hash_flag(flag) == state.flag_hash

# ===================== CHALLENGE REGISTRY =====================

CHALLENGES = [
    {
        "id": "cat_file",
        "title": "Display file content",
        "request": [
            "A file has been created in the workspace.",
            "Display its contents using the appropriate command.",
            "The flag is a single word written inside the file."
        ],
        "setup": setup_cat_file,
        "evaluate": check_cat_file,
    },
    {
        "id": "deepest",
        "title": "Find the deepest directory",
        "request": [
            "Three directories were created, one inside another, inside workspace.",
            "Find the deepest one. The flag is its name."
        ],
        "setup": setup_find_deepest_directory,
        "evaluate": check_find_deepest_directory,
    },
    {
        "id": "tab_completion",
        "title": "Advanced tab completion with ambiguity",
        "request": [
            "Four directories were created, one inside another.",
            "The first three levels use extremely ambiguous directory names.",
            "At the first two levels, there are TWO directories:",
            "only one continues the path, the other is empty.",
            "You must type at least one character before using TAB.",
            "The flag is the name of the deepest directory."
        ],
        "setup": setup_tab_completion_puzzle,
        "evaluate": check_tab_completion_puzzle,
    },
    {
        "id": "cd_maze",
        "title": "Navigate a directory maze using cd",
        "request": [
            "Navigate the directory maze using 'cd'.\n"
            "There are multiple paths, but only one leads to the deepest directory.\n"
            "The name of that directory is the flag."
        ],
        "setup": setup_cd_maze,
        "evaluate": check_cd_maze,
    },
    {
        "id": "cd_permissions",
        "title": "Change directory with restricted permissions",
        "request": [
            "You cannot list directories.",
            f"Read {INSTRUCTIONS} and use 'cd'.",
            "The flag is the deepest directory name.",
            "Use pwd anytime."
        ],
        "setup": setup_cd_permissions_puzzle,
        "evaluate": check_cd_permissions_puzzle,
    },
]

# ===================== MAIN =====================

def main():
    random.seed(time.time())
    args = init_argparser().parse_args()

    state = load_state() or State()

    if args.command == "done":
        make_writable_recursive(Path(WORKSPACE_DIR))
        make_writable_recursive(CONFIG_DIR)
        shutil.rmtree(WORKSPACE_DIR, ignore_errors=True)
        shutil.rmtree(CONFIG_DIR, ignore_errors=True)
        print("Quest cancelled.")
    elif args.command == "list":
        for i, c in enumerate(CHALLENGES):
            marker = ">" if i == state.challenge_index else " "
            print(f"{marker} {i+1}. {c['title']}")
    elif args.command == "current":
        if state.challenge_index >= len(CHALLENGES):
            print("All challenges completed.")
        else:
            print(f"Challenge {state.challenge_index + 1}:")
            print("\n".join(CHALLENGES[state.challenge_index]["request"]))
    elif args.command == "start":
        state.challenge_index = 0
        CHALLENGES[0]["setup"](state)
        save_state(state)
        print(f"Challenge {state.challenge_index + 1}:")
        print("\n".join(CHALLENGES[0]["request"]))
    elif args.command == "submit":
        if state.challenge_index >= len(CHALLENGES):
            print("All challenges completed.")
            return

        challenge = CHALLENGES[state.challenge_index]
        if not challenge["evaluate"](state, args.flag):
            print("Wrong flag.")
            return

        print("Correct!")
        state.challenge_index += 1
        save_state(state)

        if state.challenge_index < len(CHALLENGES):
            CHALLENGES[state.challenge_index]["setup"](state)
            save_state(state)
            print(f"Challenge {state.challenge_index + 1}:")
            print("\n".join(CHALLENGES[state.challenge_index]["request"]))
        else:
            print("You completed all challenges!")
    elif args.command == "goto":
        idx = resolve_challenge_index(args.target)
        if idx is None:
            print("Invalid challenge.")
            return

        state.challenge_index = idx
        CHALLENGES[idx]["setup"](state)
        save_state(state)

        print(f"Jumped to challenge {idx + 1}\n")
        print(f"Challenge {state.challenge_index + 1}:")
        print("\n".join(CHALLENGES[idx]["request"]))


if __name__ == "__main__":
    main()
