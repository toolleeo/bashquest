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
USER_CONFIG_FILE = CONFIG_DIR / "env"
SYSTEM_CONFIG_FILE = Path("/etc/bashquest/env")

CHALLENGES_TOML = "challenges.toml"
DEFAULT_WORKSPACE_NAME = "workspace"


def load_secret_key() -> bytes:
    env_file = SYSTEM_CONFIG_FILE
    # check for system configuration
    if not env_file.exists():
        env_file = USER_CONFIG_FILE
    # create local configuration if it does not exist
    if not env_file.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with env_file.open("w") as f:
            f.write("SECRET_KEY=bashquest_internal_secret_please_change_me\n")

    # read secret key
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

# ===================== ARGPARSE =====================


def init_argparser():
    parser = argparse.ArgumentParser(description="Shell quest (CTF-style)")
    sub = parser.add_subparsers(dest="command", required=True)

    parser.add_argument(
        "--seed",
        type=int,
        help="random seed for deterministic execution"
    )

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

def get_fernet(secret_key: str):
    # SECRET_KEY must be 32 bytes for Fernet
    key = secret_key.ljust(32, b'\0')[:32]
    return Fernet(base64.urlsafe_b64encode(key))


def workspace_state_file(ws: Path) -> Path:
    return ws / ".bashquest" / "state.bin"


def save_state(state: State, secret_key: str):
    ws = Path(state.workspace)
    ws_bash = ws / ".bashquest"
    ws_bash.mkdir(parents=True, exist_ok=True)
    fernet = get_fernet(secret_key)
    raw = pickle.dumps(state)
    encrypted = fernet.encrypt(raw)
    with workspace_state_file(ws).open("wb") as f:
        f.write(encrypted)

def load_state(ws: Path, secret_key: str) -> State | None:
    f = workspace_state_file(ws)
    try:
        fernet = get_fernet(secret_key)
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
    config_file = CONFIG_DIR / CHALLENGES_TOML
    if not config_file.exists():
        script_dir = Path(__file__).resolve().parent
        fallback = script_dir / CHALLENGES_TOML
        if fallback.exists():
            config_file = fallback
        else:
            print(f"Fatal error: {CHALLENGES_TOML} not found.")
            print(f"Checked:")
            print(f"  - {CONFIG_DIR / CHALLENGES_TOML}")
            print(f"  - {fallback}")
            sys.exit(1)

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


def display_challenge(state, c):
    print(80*"-")
    print(f"Challenge {state.challenge_index + 1}: {c.title}\n")
    print("\n".join(render_description(c.description, state)))
    print(80*"-")


# ===================== commands =====================

def exec_use_command(args):
    path = Path(args.path)
    if not path.is_absolute():
        path = Path.cwd() / path
    ws = path.resolve()
    if not (ws / ".bashquest").exists():
        print(f"No workspace found at {ws}")
        return
    set_active_workspace(ws)
    print(f"Active workspace set to {ws}")

def exec_workspace_command():
    ws = get_active_workspace()
    if ws is None:
        print("No active workspace. Use 'start' or 'use' to select a workspace.")
    else:
        print(ws)

def exec_done_command():
    ws = get_active_workspace()
    make_writable_recursive(ws)
    shutil.rmtree(ws, ignore_errors=True)
    print(f"Workspace {ws} removed.")

def exec_list_command(state, challenges):
    total = len(challenges)
    width = len(str(total))  # number of digits of the largest index

    for i, c in enumerate(challenges):
        marker = ">" if i == state.challenge_index else " "
        status = "[*]" if c.id in state.passed_challenges else "[ ]"
        idx = f"{i + 1:>{width}}"
        print(f"{marker} {idx}. {status} {c.title}")

def exec_challenge_command(state, challenges):
    if state.challenge_index >= len(challenges):
        print("All challenges completed.")
    else:
        c = challenges[state.challenge_index]
        display_challenge(state, c)


def exec_start_command(args, challenges, secret_key):
    # 1. Resolve and activate workspace
    path = Path(args.path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.mkdir(parents=True, exist_ok=True)
    workspace = path.resolve()
    (workspace / ".bashquest").mkdir(exist_ok=True)
    set_active_workspace(workspace)

    # 2. Load or initialize state
    state = load_state(workspace, secret_key)
    if not state:
        state = State()
        state.workspace = str(workspace)

    # 3. Start from challenge 0
    set_challenge(state, challenges, 0, secret_key)

# ===================== main =====================


def set_challenge(state: State, challenges, idx: int, secret_key):
    """
    Set the current challenge to idx:
    - reset workspace
    - run setup
    - persist state
    - print challenge header and description
    """
    if not (0 <= idx < len(challenges)):
        print("Invalid challenge.")
        return

    state.challenge_index = idx

    ws = Path(state.workspace).resolve()
    reset_workspace(ws)

    ch = challenges[idx]
    state = ch.setup(state)
    save_state(state, secret_key)

    display_challenge(state, ch)


def main():
    parser = init_argparser()
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else int(time.time())
    random.seed(seed)

    secret_key = load_secret_key()
    CHALLENGES = load_challenges()

    if args.command == "start":
        exec_start_command(args, CHALLENGES, secret_key)
        return

    workspace = get_active_workspace()
    if workspace is None:
        print("No active workspace. Use 'start' or 'use' to select a workspace.")
        return

    state = load_state(workspace, secret_key)
    if not state:
        state = State()
        state.workspace = str(workspace)
        save_state(state, secret_key)

    if args.command == "done":
        exec_done_command()
    elif args.command == "use":
        exec_use_command(args)
    elif args.command == "workspace":
        exec_workspace_command()
    elif args.command == "list":
        exec_list_command(state, CHALLENGES)
    elif args.command == "challenge":
        exec_challenge_command(state, CHALLENGES)
    elif args.command == "goto":
        idx = resolve_challenge_index(args.target, CHALLENGES)
        if idx is None:
            print("Invalid challenge.")
            return
        set_challenge(state, CHALLENGES, idx, secret_key)
    elif args.command == "submit":
        if state.challenge_index >= len(CHALLENGES):
            print("All challenges completed.")
            return

        ch = CHALLENGES[state.challenge_index]

        # Determine flag
        if getattr(ch, "requires_flag", True):
            if args.flag is None:
                print("This challenge requires a flag argument.")
                return
            flag_value = args.flag
        else:
            flag_value = None

        if not ch.evaluate(state, flag_value):
            print("Wrong flag.")
            return

        print("Correct!\n")

        # Mark challenge as passed
        state.passed_challenges.add(ch.id)
        save_state(state, secret_key)

        next_idx = state.challenge_index + 1

        if next_idx < len(CHALLENGES):
            set_challenge(state, CHALLENGES, next_idx, secret_key)
        else:
            print("You completed all challenges!")


if __name__ == "__main__":
    main()
