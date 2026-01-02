from challenges.base import BaseChallenge
import random
import string
from pathlib import Path
from state import State

USERS = ["alice", "bob", "charlie", "diana", "eve"]
TOP_FOLDERS = ["documents", "photos", "music", "downloads", "projects"]
SUBFOLDERS = ["work", "personal", "archive", "2022", "2023", "misc"]
GENERIC_FILES = ["notes.txt", "todo.md", "image.jpg", "song.mp3", "data.csv"]

class AbsolutePathsChallenge(BaseChallenge):
    id = "absolute_paths"
    title = "Find a file using absolute paths"
    description = [
        "A directory tree has been created in the workspace.",
        "Inside this tree, a *single unique file* exists.",
        "",
        "Find the *absolute path* of the following file:",
        "  {target_file}",
        "",
        "The flag is the absolute path to the file."
    ]
    requires_flag = True

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        all_dirs = []

        # Build directory tree
        for user in random.sample(USERS, k=3):
            for folder in random.sample(TOP_FOLDERS, k=random.randint(2, 3)):
                for sub in random.sample(SUBFOLDERS, k=random.randint(1, 2)):
                    dir_path = ws / user / folder / sub
                    dir_path.mkdir(parents=True, exist_ok=True)
                    all_dirs.append(dir_path)

                    # Create generic files (non-unique)
                    #for fname in random.sample(GENERIC_FILES, k=random.randint(1, 3)):
                    #    (dir_path / fname).touch()

        # Create a unique target file in exactly one directory
        target_name = "target.txt"
        target_dir = random.choice(all_dirs)
        target_path = target_dir / target_name
        target_path.touch()

        # Persist state
        state.target_file = target_name
        state.absolute_path_flag = str(target_path.resolve())

        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return flag.strip() == state.absolute_path_flag
