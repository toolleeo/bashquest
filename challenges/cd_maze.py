from pathlib import Path
from state import State
from utils import hash_flag, WORKSPACE_DIR

# Challenge metadata
title_cd_maze = "Navigate a directory maze using cd"
description_cd_maze = [
    "Navigate the directory maze using 'cd'.",
    "There are multiple paths, but only one leads to the deepest directory.",
    "The name of that directory is the flag."
]

# Setup function
def setup_cd_maze(state: State):
    ws = Path(WORKSPACE_DIR).resolve()

    start = ws / "start"
    go_left = start / "go_left"
    go_right = start / "go_right"
    treasure = go_left / "treasure"
    deadend = go_right / "deadend"

    treasure.mkdir(parents=True)
    deadend.mkdir(parents=True)

    state.flag_hash = hash_flag("treasure")
    state.workspace = str(ws)
    return state

# Evaluation function
def check_cd_maze(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash

