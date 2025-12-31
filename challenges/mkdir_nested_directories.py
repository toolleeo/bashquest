from pathlib import Path
import random
from state import State

DIR_NAMES = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "omega",
]

# ---------- REQUIRED PLUGIN SYMBOLS ----------

requires_flag_mkdir_nested_directories = False

title_mkdir_nested_directories = "Create nested directories"

description_mkdir_nested_directories = [
    "Create three directories, one inside another, inside the workspace.",
    "The directories must be named (in this order): {dir1}/{dir2}/{dir3}.",
    "The flag is the presence of this directory structure."
]

def setup_mkdir_nested_directories(state: State) -> State:
    # Choose three distinct directory names
    dir1, dir2, dir3 = random.sample(DIR_NAMES, 3)

    # Persist visible data
    state.dir1 = dir1
    state.dir2 = dir2
    state.dir3 = dir3

    return state


def check_mkdir_nested_directories(state: State, flag: str | None) -> bool:
    ws = Path(state.workspace)

    target = ws / state.dir1 / state.dir2 / state.dir3

    # Final directory must exist
    if not target.exists():
        return False

    if not target.is_dir():
        return False

    return True

