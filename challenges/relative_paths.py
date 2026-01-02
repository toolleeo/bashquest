from challenges.base import BaseChallenge
import random
from pathlib import Path
from state import State

USERS = ["alice", "bob", "charlie", "diana", "eve"]
TOP_FOLDERS = ["documents", "photos", "music", "downloads", "projects"]
SUBFOLDERS = ["work", "personal", "archive", "2022", "2023", "misc"]
FILES = ["notes.txt", "todo.md", "image.jpg", "song.mp3", "data.csv"]

class RelativePathsChallenge(BaseChallenge):
    id = "relative_paths"
    title = "Navigate using relative paths"
    description = [
        "A directory tree has been created in the workspace.",
        "You are currently located in the directory:",
        "  {start_dir}",
        "",
        "What is the *relative path* from this directory to:",
        "  {target_dir}",
        "",
        "The flag is the relative path."
        "Note: the path MUST be the shortest possible one.",
    ]
    requires_flag = True

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        # Pick structure
        user_dirs = random.sample(USERS, k=3)
        tree = {}

        for user in user_dirs:
            folders = random.sample(TOP_FOLDERS, k=random.randint(2, 4))
            tree[user] = {}
            for folder in folders:
                subs = random.sample(SUBFOLDERS, k=random.randint(1, 2))
                tree[user][folder] = subs

        # Create directories
        for user, folders in tree.items():
            for folder, subs in folders.items():
                for sub in subs:
                    path = ws / user / folder / sub
                    path.mkdir(parents=True, exist_ok=True)

                    # Add random empty files
                    #for fname in random.sample(FILES, k=random.randint(0, 2)):
                    #    (path / fname).touch()

        # Choose start and target (different branches, same user)
        user = random.choice(user_dirs)
        folders = list(tree[user].keys())

        start_folder, target_folder = random.sample(folders, 2)
        start_sub = random.choice(tree[user][start_folder])
        target_sub = random.choice(tree[user][target_folder])

        start_path = Path(user) / start_folder / start_sub
        target_path = Path(user) / target_folder / target_sub

        # Compute correct relative path
        relative = Path("..") / ".." / target_folder / target_sub

        # Persist state
        state.start_dir = str(start_path)
        state.target_dir = str(target_path)
        state.relative_path_flag = str(relative)

        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return flag.strip() == state.relative_path_flag
