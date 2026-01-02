from challenges.base import BaseChallenge
import random
from pathlib import Path
from state import State
from utils import hash_flag

FRUITS = [
    "apple", "banana", "orange", "grape", "lemon",
    "peach", "pear", "plum", "mango", "papaya",
    "kiwi", "melon", "cherry", "fig", "date",
    "apricot", "avocado", "coconut", "lime", "guava",
    "raspberry", "blueberry", "blackberry", "cranberry",
    "pineapple", "nectarine", "pomegranate", "tangerine",
]

FIRST_NAMES = [
    "alice", "bob", "carol", "david", "emma",
    "frank", "grace", "henry", "irene", "jack",
    "kate", "leo", "maria", "nathan", "olivia",
    "paul", "quinn", "rachel", "sam", "tina",
    "ursula", "victor", "wendy", "xavier", "yvonne",
    "zach", "luca", "sofia", "marco", "elena",
]


class CopyFileToDirChallenge(BaseChallenge):
    id = "cp_copy_file_to_dir"
    title = "Copy a file into a directory"
    requires_flag = False

    description = [
        "The workspace contains one file and one directory.",
        "Copy the file into the directory.",
        "The challenge is completed when the file exists inside the directory."
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        fruit = random.choice(FRUITS)
        name = random.choice(FIRST_NAMES)

        src_file = ws / f"{fruit}.txt"
        dest_dir = ws / name

        # Create file and directory
        src_file.write_text(f"This file is named {fruit}.\n")
        dest_dir.mkdir(exist_ok=True)

        # Persist state
        state.cp_source_file = src_file.name
        state.cp_dest_dir = dest_dir.name

        return state

    def evaluate(self, state: State, flag: str | None) -> bool:
        ws = Path(state.workspace)

        src = ws / state.cp_source_file
        dest = ws / state.cp_dest_dir / state.cp_source_file

        # Source must still exist
        if not src.exists() or not src.is_file():
            return False

        # Destination must contain a copied file
        if not dest.exists() or not dest.is_file():
            return False

        # Optional: ensure content matches
        try:
            return src.read_text() == dest.read_text()
        except Exception:
            return False

