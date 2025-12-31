#!/usr/bin/env python3

import argparse
import stat
import shutil
import random
import time
import pickle
import hashlib
from pathlib import Path
import importlib
import tomllib
from challenges.base import BaseChallenge
from utils import reset_workspace, make_writable_recursive

# ===================== CONFIG =====================

CONFIG_DIR = Path.home() / ".config" / "bashquest"
WORKSPACE_DIR = "workspace"

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

def render_description(description: list[str], state: State) -> list[str]:
    context = vars(state)   # ← magic line

    rendered = []
    for line in description:
        try:
            rendered.append(line.format(**context))
        except KeyError:
            rendered.append(line)

    return rendered

def resolve_challenge_index(target: str, challenges) -> int | None:
    # numeric (1-based)
    if target.isdigit():
        idx = int(target) - 1
        if 0 <= idx < len(challenges):
            return idx
        return None

    # by id
    for i, c in enumerate(challenges):
        if c.id == target:
            return i
    return None


class SymbolChallenge:
    def __init__(self, cid, title, description, setup, evaluate):
        self.id = cid
        self.title = title
        self.description = description
        self.setup = setup
        self.evaluate = evaluate


def build_from_symbols(mod, cid):
    try:
        title = getattr(mod, f"title_{cid}")
        description = getattr(mod, f"description_{cid}")
        setup = getattr(mod, f"setup_{cid}")
        evaluate = getattr(mod, f"check_{cid}")
    except AttributeError as e:
        raise RuntimeError(
            f"Challenge '{cid}' is missing a required symbol: {e}"
        )

    if not isinstance(description, list):
        raise RuntimeError(
            f"description_{cid} must be a list of strings"
        )

    return SymbolChallenge(
        cid=cid,
        title=title,
        description=description,
        setup=setup,
        evaluate=evaluate,
    )

def load_challenges():
    data = tomllib.loads(Path(CONFIG_DIR / Path("challenges.toml")).read_text())
    challenge_ids = data["challenges"]

    challenges = []

    for cid in challenge_ids:
        mod = importlib.import_module(f"challenges.{cid}")

        if hasattr(mod, "Challenge"):
            challenges.append(mod.Challenge())
        else:
            challenges.append(build_from_symbols(mod, cid))

    return challenges

# ===================== MAIN =====================

def main():
    random.seed(time.time())

    parser = init_argparser()
    args = parser.parse_args()

    CHALLENGES = load_challenges()

    state = load_state()
    if not state:
        state = State()
        save_state(state)

    cmd = args.command

    if cmd == "done":
        make_writable_recursive(Path(WORKSPACE_DIR))
        shutil.rmtree(WORKSPACE_DIR, ignore_errors=True)
        print("Quest cancelled.")

    elif cmd == "list":
        for i, c in enumerate(CHALLENGES):
            marker = ">" if i == state.challenge_index else " "
            print(f"{marker} {i+1}. {c.title}")

    elif cmd == "current":
        if state.challenge_index >= len(CHALLENGES):
            print("All challenges completed.")
        else:
            c = CHALLENGES[state.challenge_index]
            print(f"Challenge {state.challenge_index + 1}: {c.title}\n")
            print("\n".join(render_description(c.description, state)))


    elif cmd == "start":
        state.challenge_index = 0
        ws = Path(WORKSPACE_DIR).resolve()
        reset_workspace(ws)
        state.workspace = str(ws)

        ch = CHALLENGES[0]
        state = ch.setup(state)
        save_state(state)

        print(f"Challenge 1: {ch.title}\n")
        print("\n".join(render_description(ch.description, state)))

    elif cmd == "goto":
        idx = resolve_challenge_index(args.target, CHALLENGES)
        if idx is None:
            print("Invalid challenge.")
            return

        state.challenge_index = idx
        ws = Path(WORKSPACE_DIR).resolve()
        reset_workspace(ws)
        state.workspace = str(ws)

        ch = CHALLENGES[idx]
        state = ch.setup(state)
        save_state(state)

        print(f"Jumped to challenge {idx + 1}: {ch.title}\n")
        print("\n".join(render_description(ch.description, state)))

    elif cmd == "submit":
        if state.challenge_index >= len(CHALLENGES):
            print("All challenges completed.")
            return

        ch = CHALLENGES[state.challenge_index]
        if not ch.evaluate(state, args.flag):
            print("Wrong flag.")
            return

        print("Correct!\n")
        state.challenge_index += 1
        save_state(state)

        if state.challenge_index < len(CHALLENGES):
            next_ch = CHALLENGES[state.challenge_index]
            ws = Path(WORKSPACE_DIR).resolve()
            reset_workspace(ws)
            state.workspace = str(ws)

            state = next_ch.setup(state)
            save_state(state)

            print(f"Challenge {state.challenge_index + 1}: {next_ch.title}\n")
            print("\n".join(render_description(next_ch.description, state)))
        else:
            print("You completed all challenges!")


if __name__ == "__main__":
    main()
