import random
from pathlib import Path
from state import State
from utils import hash_flag, short_names

# Challenge metadata
title_tab_completion = "Advanced tab completion with ambiguity"
description_tab_completion = [
    "Four directories were created, one inside another.",
    "The first three levels use extremely ambiguous directory names.",
    "At the first two levels, there are TWO directories:",
    "only one continues the path, the other is empty.",
    "You must type at least one character before using TAB.",
    "The flag is the name of the deepest directory."
]

# Helper
def random_ambiguous_name(length=20):
    chars = ["0", "O", "1", "l"]
    return "".join(random.choice(chars) for _ in range(length))

# Setup function
def setup_tab_completion(state: State):
    ws = Path(state.workspace).resolve()

    # Level 1
    d1_main = random_ambiguous_name()
    d1_fake = random_ambiguous_name()
    p1_main = ws / d1_main
    p1_fake = ws / d1_fake
    p1_main.mkdir()
    p1_fake.mkdir()

    # Level 2 (only under main path)
    d2_main = random_ambiguous_name()
    d2_fake = random_ambiguous_name()
    p2_main = p1_main / d2_main
    p2_fake = p1_main / d2_fake
    p2_main.mkdir()
    p2_fake.mkdir()

    # Level 3
    d3 = random_ambiguous_name()
    p3 = p2_main / d3
    p3.mkdir()

    # Level 4 (flag)
    d4 = random.choice(short_names)
    p4 = p3 / d4
    p4.mkdir()

    state.flag_hash = hash_flag(d4)
    state.workspace = str(ws)
    return state

# Evaluation function
def check_tab_completion(state: State, flag: str) -> bool:
    return hash_flag(flag) == state.flag_hash
