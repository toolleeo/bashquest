from challenges.base import BaseChallenge
import random
from pathlib import Path
from state import State
from utils import hash_flag, WORKSPACE_DIR

possible_flags = [
    "hello",
    "banana",
    "penguin",
    "ocean",
    "terminal",
    "kernel",
]

class CatFileChallenge(BaseChallenge):
    id = "cat_file"
    title = "Display file content"
    description = [
        "A file has been created in the workspace.",
        "Display its contents using the appropriate command.",
        "The flag is a single word written inside the file."
    ]
    requires_flag = True  # Optional, defaults to True

    def setup(self, state: State) -> State:
        ws = Path(WORKSPACE_DIR).resolve()

        flag = random.choice(possible_flags)

        file_path = ws / "message.txt"
        file_path.write_text(
            "The flag is the word below:\n"
            f"{flag}\n"
        )

        state.flag_hash = hash_flag(flag)
        state.workspace = str(ws)
        state.current_flag_word = flag  # store plain word if needed
        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag) == state.flag_hash

