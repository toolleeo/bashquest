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

requires_flag_mkdir_single_directory = False

title_mkdir_single_directory = "Create a directory"

description_mkdir_single_directory = [
    "Create a single directory inside the workspace named: {dir_name}.",
    "The flag is the presence of this directory."
]

def setup_mkdir_single_directory(state: State) -> State:
    # Choose directory name
    name = random.choice(DIR_NAMES)

    # Persist visible data
    state.dir_name = name

    return state


def check_mkdir_single_directory(state: State, flag: str | None) -> bool:
    ws = Path(state.workspace)
    target = ws / state.dir_name

    # Directory must exist and be exactly one level deep
    if not target.exists():
        return False

    if not target.is_dir():
        return False

    return True

