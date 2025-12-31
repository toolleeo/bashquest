import random
from pathlib import Path
from state import State
from utils import hash_flag, short_names

# Challenge metadata
title_deepest_directory = "Find the deepest directory"

description_deepest_directory = [
    "Three directories were created, one inside another, inside workspace.",
    "Find the deepest one. The flag is its name."
]

# Setup function
def setup_deepest_directory(state: State):
    ws = Path(state.workspace).resolve()

    d1, d2, d3 = random.sample(short_names, 3)
    (ws / d1 / d2 / d3).mkdir(parents=True)

    state.flag_hash = hash_flag(d3)
    state.workspace = str(ws)
    return state

# Evaluation function
def check_deepest_directory(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash

