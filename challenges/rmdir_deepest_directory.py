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

requires_flag_rmdir_deepest_directory = False

title_rmdir_deepest_directory = "Remove the deepest directory"

description_rmdir_deepest_directory = [
    "Three directories were created, one inside another, inside the workspace.",
    "Remove only the deepest directory using rmdir.",
    "The directory to remove is: {dir1}/{dir2}/{dir3}.",
    "The parent directories must remain."
]

def setup_rmdir_deepest_directory(state: State) -> State:
    ws = Path(state.workspace)

    # Choose three distinct directory names
    dir1, dir2, dir3 = random.sample(DIR_NAMES, 3)

    # Create nested directories
    deepest = ws / dir1 / dir2 / dir3
    deepest.mkdir(parents=True, exist_ok=True)

    # Persist visible data
    state.dir1 = dir1
    state.dir2 = dir2
    state.dir3 = dir3

    return state


def check_rmdir_deepest_directory(state: State, flag: str | None) -> bool:
    ws = Path(state.workspace)

    d1 = ws / state.dir1
    d2 = d1 / state.dir2
    d3 = d2 / state.dir3

    # Deepest directory must be removed
    if d3.exists():
        return False

    # Parent directories must still exist
    if not d2.exists() or not d2.is_dir():
        return False

    if not d1.exists() or not d1.is_dir():
        return False

    return True

