from pathlib import Path
import random
from state import State

# ---------- Metadata ----------
title_cd_maze = "Navigate a directory maze"
description_cd_maze = [
    "Navigate the directory maze.",
    "There are multiple paths, but only one leads to the deepest directory.",
    "The name of such deepest directory is the flag."
]

# List of 20 possible flag names
FLAG_NAMES = [
    "alpha", "bravo", "charlie", "delta", "echo",
    "foxtrot", "golf", "hotel", "india", "juliet",
    "kilo", "lima", "mike", "november", "oscar",
    "papa", "quebec", "romeo", "sierra", "tango"
]

def setup_cd_maze(state: State) -> State:
    ws = Path(state.workspace).resolve()

    # Create top-level directories
    top_dirs = ["1_one", "2_two", "3_three"]
    for d in top_dirs:
        (ws / d).mkdir(exist_ok=True)

    # Randomly pick one as the correct path
    correct_top = random.choice(top_dirs)
    remaining_dirs = [d for d in top_dirs if d != correct_top]

    # In the correct directory, create go_deeper/<flag_name>
    flag_name = random.choice(FLAG_NAMES)
    correct_path = ws / correct_top / "go_deeper" / flag_name
    correct_path.mkdir(parents=True)

    # In the other directories, create deadend
    for d in remaining_dirs:
        (ws / d / "deadend").mkdir(parents=True)

    # Persist state
    state.workspace = str(ws)
    state.cd_maze_flag_name = flag_name  # store for display if needed
    return state

def check_cd_maze(state: State, flag: str) -> bool:
    return flag == state.cd_maze_flag_name
