import stat
import random
from pathlib import Path
from state import State
from utils import hash_flag

INSTRUCTIONS = "INSTRUCTIONS.txt"

def random_dirname(n=6):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.choice(chars) for _ in range(n))

# ---------- REQUIRED PLUGIN SYMBOLS ----------

title_cd_permissions = "Change directory with restricted permissions"

description_cd_permissions = [
    "You cannot list directories.",
    f"Read {INSTRUCTIONS} (autocompletion is disabled) and use 'cd'.",
    "The flag is the deepest directory name.",
    "Use pwd anytime."
]

def setup_cd_permissions(state: State) -> State:
    """
    Set up the directory structure for the permissions puzzle.
    Returns the modified state; main handles workspace and saving.
    """
    ws = Path(state.workspace).resolve()

    d1, d2, d3 = random_dirname(), random_dirname(), random_dirname()
    p1, p2, p3 = ws / d1, ws / d1 / d2, ws / d1 / d2 / d3
    p3.mkdir(parents=True)

    (p1 / INSTRUCTIONS).write_text(f"To continue, cd into:\n{d2}\n")
    (p2 / INSTRUCTIONS).write_text(f"To continue, cd into:\n{d3}\n")
    (p3 / INSTRUCTIONS).write_text(
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
    return state

def check_cd_permissions(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash
