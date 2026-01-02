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

class CopyAndRenameFileChallenge(BaseChallenge):
    id = "copy_file_in_same_directory"
    title = "Copy a file in the same directory"
    requires_flag = False

    description = [
        "The workspace contains one file.",
        "",
        "Create a copy of the file in the same directory.",
        "The name of the file must be:",
        "  {cp_dst}",
        "",
        "The challenge is completed when BOTH files exist."
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        src_name, dst_name = random.sample(FRUITS, 2)

        src_file = ws / f"{src_name}.txt"
        dst_file = ws / f"{dst_name}.txt"

        # Create source file
        src_file.write_text(f"This file is named {src_name}.\n")

        # Persist expected names
        state.cp_src = src_file.name
        state.cp_dst = dst_file.name

        return state

    def evaluate(self, state: State, flag: str | None) -> bool:
        ws = Path(state.workspace)

        src = ws / state.cp_src
        dst = ws / state.cp_dst

        # Both files must exist
        if not src.exists() or not dst.exists():
            return False

        # They must be files
        if not src.is_file() or not dst.is_file():
            return False

        # Content must be identical (true copy, not mv)
        try:
            return src.read_text() == dst.read_text()
        except Exception:
            return False

