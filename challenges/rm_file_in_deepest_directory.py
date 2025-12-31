from pathlib import Path
import random
import string
from state import State

DIR_NAMES = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "omega",
]

# ---------- REQUIRED PLUGIN SYMBOLS ----------

requires_flag_rm_file_in_deepest_directory = False

title_rm_file_in_deepest_directory = "Remove a file in the deepest directory"

description_rm_file_in_deepest_directory = [
    "Three directories were created, one inside another, inside the workspace.",
    "Inside the deepest directory there is a file named: {filename}.",
    "Remove ONLY this file.",
    "All directories must remain."
]

def setup_rm_file_in_deepest_directory(state: State) -> State:
    ws = Path(state.workspace)

    # Pick directory names
    dir1, dir2, dir3 = random.sample(DIR_NAMES, 3)

    # Generate random filename
    filename = "".join(random.choices(string.ascii_lowercase, k=8)) + ".txt"

    deepest = ws / dir1 / dir2 / dir3
    deepest.mkdir(parents=True, exist_ok=True)

    # Create file
    file_path = deepest / filename
    file_path.write_text("temporary file\n")

    # Persist visible state
    state.dir1 = dir1
    state.dir2 = dir2
    state.dir3 = dir3
    state.filename = filename

    return state


def check_rm_file_in_deepest_directory(state: State, flag: str | None) -> bool:
    ws = Path(state.workspace)

    d1 = ws / state.dir1
    d2 = d1 / state.dir2
    d3 = d2 / state.dir3
    file_path = d3 / state.filename

    # File must be removed
    if file_path.exists():
        return False

    # All directories must still exist
    if not d3.is_dir():
        return False
    if not d2.is_dir():
        return False
    if not d1.is_dir():
        return False

    return True

