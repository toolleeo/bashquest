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

FIRST_NAMES = [
    "alice", "bob", "carol", "dave", "eve",
    "frank", "grace", "heidi", "ivan", "judy",
    "mallory", "oscar", "peggy", "trent", "victor",
    "walter", "sybil", "nina", "louis", "paul",
    "mark", "julia", "lucas", "anna", "emma",
    "noah", "liam", "olivia", "mia", "sophia",
]

class MoveFileIntoDirectoryChallenge(BaseChallenge):
    id = "move_file_into_directory"
    title = "Move a file into a directory"
    requires_flag = False

    description = [
        "The workspace contains one file and one directory.",
        "",
        "Move the file into the directory.",
        "",
        "The challenge is completed when the file exists",
        "inside the directory and no longer exists",
        "in the workspace root."
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        file_name = random.choice(FRUITS)
        dir_name = random.choice(FIRST_NAMES)

        src_file = ws / f"{file_name}.txt"
        target_dir = ws / dir_name

        # Create filesystem
        src_file.write_text(f"This file is named {file_name}.\n")
        target_dir.mkdir(exist_ok=True)

        # Persist expected state
        state.mv_src = src_file.name
        state.mv_dir = dir_name

        return state

    def evaluate(self, state: State, flag: str | None) -> bool:
        ws = Path(state.workspace)

        src = ws / state.mv_src
        dst = ws / state.mv_dir / state.mv_src

        # Source must NOT exist anymore
        if src.exists():
            return False

        # Destination must exist
        if not dst.exists() or not dst.is_file():
            return False

        return True

