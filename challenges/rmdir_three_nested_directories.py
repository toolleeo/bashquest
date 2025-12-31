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

requires_flag_rmdir_three_nested_directories = False

title_rmdir_three_nested_directories = "Remove three nested directories"

description_rmdir_three_nested_directories = [
    "Three directories were created, one inside another, inside the workspace.",
    "Remove all three directories.",
    "At the end, none of the three directories must exist.",
    "Can you do it with one single command?"
]

def setup_rmdir_three_nested_directories(state: State) -> State:
    ws = Path(state.workspace)

    # Pick directory names
    dir1, dir2, dir3 = random.sample(DIR_NAMES, 3)

    deepest = ws / dir1 / dir2 / dir3
    deepest.mkdir(parents=True, exist_ok=True)

    # Persist visible state
    state.dir1 = dir1
    state.dir2 = dir2
    state.dir3 = dir3

    return state


def check_rmdir_three_nested_directories(state: State, flag: str | None) -> bool:
    ws = Path(state.workspace)

    d1 = ws / state.dir1
    d2 = d1 / state.dir2
    d3 = d2 / state.dir3

    # None of the directories must exist
    return not d1.exists() and not d2.exists() and not d3.exists()
