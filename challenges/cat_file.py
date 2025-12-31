import random
from pathlib import Path
from state import State
from utils import hash_flag, WORKSPACE_DIR

# Challenge metadata
title_cat_file = "Display file content"
description_cat_file = [
    "A file has been created in the workspace.",
    "Display its contents using the appropriate command.",
    "The flag is a single word written inside the file."
]

# Setup function
def setup_cat_file(state: State):
    ws = Path(WORKSPACE_DIR).resolve()

    possible_flags = [
        "hello",
        "banana",
        "penguin",
        "ocean",
        "terminal",
        "kernel",
    ]
    flag = random.choice(possible_flags)

    file_path = ws / "message.txt"
    file_path.write_text(
        "The flag is the word below:\n"
        f"{flag}\n"
    )

    state.flag_hash = hash_flag(flag)
    state.workspace = str(ws)
    return state

# Evaluation function
def check_cat_file(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash

