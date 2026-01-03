from challenges.base import BaseChallenge
import random
from pathlib import Path
from state import State

FRUITS = [
    "apple", "banana", "orange", "grape", "lemon",
    "peach", "pear", "plum", "mango", "papaya",
    "kiwi", "melon", "cherry", "fig", "date",
    "apricot", "avocado", "coconut", "lime", "guava",
    "raspberry", "blueberry", "blackberry", "cranberry",
    "pineapple", "nectarine", "pomegranate", "tangerine",
]

class RenameFileChallenge(BaseChallenge):
    id = "mv_rename_file"
    title = "Rename a file"
    requires_flag = False

    description = [
        "The workspace contains a single file.",
        "",
        "Rename the file to another with name:",
        "  {mv_new_name}",
        "",
        "The challenge is completed when:",
        "- the original file no longer exists",
        "- the new file exists in the workspace",
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        old_name, new_name = random.sample(FRUITS, 2)

        src = ws / f"{old_name}.txt"
        src.write_text(f"This file was originally named {old_name}.\n")

        # Persist expected names
        state.mv_old_name = f"{old_name}.txt"
        state.mv_new_name = f"{new_name}.txt"

        return state

    def evaluate(self, state: State, flag: str | None) -> bool:
        ws = Path(state.workspace)

        old_file = ws / state.mv_old_name
        new_file = ws / state.mv_new_name

        # Old must not exist
        if old_file.exists():
            return False

        # New must exist
        if not new_file.exists() or not new_file.is_file():
            return False

        return True

