from challenges.base import BaseChallenge
import random
from pathlib import Path
from state import State
from utils import hash_flag

DIR_NAMES = [
    "projects", "workspace", "sandbox", "data",
    "files", "docs", "notes", "src", "build",
    "output", "results", "archive",
]

class PWDAbsolutePathChallenge(BaseChallenge):
    id = "pwd_absolute_path"
    title = "Print the working directory"
    requires_flag = True

    description = [
        "Two directories have been created, one inside the other.",
        "",
        "Change directory into the deepest one.",
        "Then print its absolute path.",
        "",
        "The flag is the absolute path of the current directory.",
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        dir1, dir2 = random.sample(DIR_NAMES, 2)

        deepest = ws / dir1 / dir2
        deepest.mkdir(parents=True)

        # Absolute path the user must discover
        abs_path = str(deepest.resolve())

        state.pwd_target_path = abs_path
        state.flag_hash = hash_flag(abs_path)

        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag.strip()) == state.flag_hash

