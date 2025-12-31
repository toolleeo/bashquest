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
import sys
import tomllib
from challenges.base import BaseChallenge
from utils import reset_workspace, make_writable_recursive
from state import State
from cryptography.fernet import Fernet
import base64

# ===================== CONFIG =====================

CONFIG_DIR = Path.home() / ".config" / "bashquest"
ACTIVE_WORKSPACE_FILE = CONFIG_DIR / "active_workspace"

DEFAULT_WORKSPACE_NAME = "workspace"


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

    start = sub.add_parser("start", help="start a new workspace")
    start.add_argument(
        "path",
        nargs="?",
        default=DEFAULT_WORKSPACE_NAME,
        help="path to workspace (relative or absolute)",
    )

    sub.add_parser("list", help="list all challenges")
    sub.add_parser("challenge", help="show current challenge")

    goto = sub.add_parser("goto", help="jump to a specific challenge (resets workspace)")
    goto.add_argument("target", help="challenge number (1-based) or challenge id")

    submit = sub.add_parser("submit", help="submit a flag")
    submit.add_argument(
        "flag",
        nargs="?",
        default=None,
        help="string to submit (optional for put-the-flag challenges)",
    )

    use = sub.add_parser("use", help="switch to another workspace")
    use.add_argument("path", help="path to workspace to use (absolute or relative)")

    sub.add_parser("workspace", help="show absolute path of current workspace")

    sub.add_parser("done", help="cancel the quest and cleanup")

    return parser


# ===================== STATE =====================

def get_fernet():
    # SECRET_KEY must be 32 bytes for Fernet
    key = SECRET_KEY.ljust(32, b'\0')[:32]
    return Fernet(base64.urlsafe_b64encode(key))

def simple_hash(state: State) -> bytes:
    h = hashlib.sha256()
    h.update(SECRET_KEY)
    h.update(state.challenge_index.to_bytes(4, "little"))
    h.update(state.flag_hash)
    h.update(state.workspace.encode())
    return h.digest()


def workspace_state_file(ws: Path) -> Path:
    return ws / ".bashquest" / "state.bin"


def save_state(state: State):
    ws = Path(state.workspace)
    ws_bash = ws / ".bashquest"
    ws_bash.mkdir(parents=True, exist_ok=True)
    fernet = get_fernet()
    raw = pickle.dumps(state)
    encrypted = fernet.encrypt(raw)
    with workspace_state_file(ws).open("wb") as f:
        f.write(encrypted)

def load_state(ws: Path) -> State | None:
    f = workspace_state_file(ws)
    try:
        fernet = get_fernet()
        raw = f.read_bytes()
        state = pickle.loads(fernet.decrypt(raw))
        return state
    except Exception:
        return None


def set_active_workspace(ws: Path):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with ACTIVE_WORKSPACE_FILE.open("w") as f:
        f.write(str(ws.resolve()))


def get_active_workspace() -> Path | None:
    if not ACTIVE_WORKSPACE_FILE.exists():
        return None
    ws = Path(ACTIVE_WORKSPACE_FILE.read_text().strip())
    if ws.exists() and ws.is_dir():
        return ws
    return None


def detect_workspace_from_cwd() -> Path | None:
    p = Path.cwd()
    while p != p.parent:
        if (p / ".bashquest").exists():
            return p
        p = p.parent
    return None


# ===================== UTIL =====================


def render_description(description: list[str], state: State) -> list[str]:
    context = vars(state)
    rendered = []
    for line in description:
        try:
            rendered.append(line.format(**context))
        except KeyError:
            rendered.append(line)
    return rendered


def resolve_challenge_index(target: str, challenges) -> int | None:
    if target.isdigit():
        idx = int(target) - 1
        if 0 <= idx < len(challenges):
            return idx
        return None
    for i, c in enumerate(challenges):
        if getattr(c, "id", None) == target:
            return i
    return None


# ===================== CHALLENGE LOADING =====================

class SymbolChallenge:
    def __init__(self, cid, title, description, setup, evaluate):
        self.id = cid
        self.title = title
        self.description = description
        self.setup = setup
        self.evaluate = evaluate


def build_from_symbols(mod, cid):
    title = getattr(mod, f"title_{cid}")
    description = getattr(mod, f"description_{cid}")
    setup = getattr(mod, f"setup_{cid}")
    evaluate = getattr(mod, f"check_{cid}")

    ch = SymbolChallenge(cid, title, description, setup, evaluate)
    ch.requires_flag = getattr(mod, f"requires_flag_{cid}", True)
    return ch


def load_challenges():
    config_file = CONFIG_DIR / "challenges.toml"
    data = tomllib.loads(config_file.read_text())
    challenge_ids = data["challenges"]

    challenges = []

    for cid in challenge_ids:
        mod = importlib.import_module(f"challenges.{cid}")

        cls = next(
            (c for c in mod.__dict__.values()
             if isinstance(c, type)
             and issubclass(c, BaseChallenge)
             and c is not BaseChallenge),
            None
        )

        if cls:
            challenges.append(cls())
        else:
            challenges.append(build_from_symbols(mod, cid))

    return challenges


# ===================== MAIN =====================


def main():
    random.seed(time.time())

    parser = init_argparser()
    args = parser.parse_args()

    CHALLENGES = load_challenges()

    # Determine workspace
    workspace: Path | None = None
    if args.command == "start":
        path = Path(args.path)
        if not path.is_absolute():
            path = Path.cwd() / path
        path.mkdir(parents=True, exist_ok=True)
        workspace = path.resolve()
        (workspace / ".bashquest").mkdir(exist_ok=True)
        set_active_workspace(workspace)
    elif args.command == "use":
        path = Path(args.path)
        if not path.is_absolute():
            path = Path.cwd() / path
        ws = detect_workspace_from_cwd() or path.resolve()
        if not (ws / ".bashquest").exists():
            print(f"No workspace found at {ws}")
            return
        set_active_workspace(ws)
        print(f"Active workspace set to {ws}")
        return
    elif args.command == "workspace":
        if state.challenge_index >= len(CHALLENGES):
            print("All challenges completed.")
        else:
            c = CHALLENGES[state.challenge_index]
            status = "✓ Passed" if c.id in state.passed_challenges else "Not passed"
            print(f"Challenge {state.challenge_index + 1}: {c.title} ({status})\n")
            print("\n".join(render_description(c.description, state)))
    else:
        workspace = detect_workspace_from_cwd() or get_active_workspace()
        if workspace is None:
            print("No active workspace. Use 'start' or 'use' to select a workspace.")
            return

    state = load_state(workspace)
    if not state:
        state = State()
        state.workspace = str(workspace)
        save_state(state)

    cmd = args.command

    if cmd == "done":
        make_writable_recursive(workspace)
        shutil.rmtree(workspace, ignore_errors=True)
        print(f"Workspace {workspace} removed.")
        return

    elif cmd == "list":
        for i, c in enumerate(CHALLENGES):
            marker = ">" if i == state.challenge_index else " "
            status = "[*]" if c.id in state.passed_challenges else "[ ]"
            print(f"{marker} {i+1}. {status} {c.title}")

    elif cmd == "challenge":
        if state.challenge_index >= len(CHALLENGES):
            print("All challenges completed.")
        else:
            c = CHALLENGES[state.challenge_index]
            print(f"Challenge {state.challenge_index + 1}: {c.title}\n")
            print("\n".join(render_description(c.description, state)))
        return

    elif cmd == "start":
        state.challenge_index = 0
        ws = workspace.resolve()
        reset_workspace(ws)
        state.workspace = str(ws)

        ch = CHALLENGES[0]
        state = ch.setup(state)
        save_state(state)

        print(f"Challenge 1: {ch.title}\n")
        print("\n".join(render_description(ch.description, state)))
        return

    elif cmd == "goto":
        idx = resolve_challenge_index(args.target, CHALLENGES)
        if idx is None:
            print("Invalid challenge.")
            return

        state.challenge_index = idx
        ws = workspace.resolve()
        reset_workspace(ws)
        state.workspace = str(ws)

        ch = CHALLENGES[idx]
        state = ch.setup(state)
        save_state(state)

        print(f"Jumped to challenge {idx + 1}: {ch.title}\n")
        print("\n".join(render_description(ch.description, state)))
        return

    elif cmd == "submit":
        ch = CHALLENGES[state.challenge_index]
        flag_value = args.flag
        if getattr(ch, "requires_flag", True) and flag_value is None:
            print("This challenge requires a flag argument.")
            return

        if not ch.evaluate(state, flag_value):
            print("Wrong flag.")
            return

        print("Correct!\n")
        state.passed_challenges.add(ch.id)  # mark challenge as passed
        state.challenge_index += 1
        save_state(state)

        if state.challenge_index < len(CHALLENGES):
            next_ch = CHALLENGES[state.challenge_index]
            ws = workspace.resolve()
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
