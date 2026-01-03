from challenges.base import BaseChallenge
import random
from pathlib import Path
from state import State

DIR_NAMES = [
    "alpha", "beta", "gamma", "delta", "epsilon",
    "omega", "sigma", "theta", "lambda", "kappa",
    "docs", "data", "config", "assets", "backup",
    "cache", "logs", "tmp", "bin", "lib",
]

class RenameDirectoryChallenge(BaseChallenge):
    id = "mv_rename_directory"
    title = "Rename a directory"
    requires_flag = False

    description = [
        "The workspace contains two directories, one inside the other.",
        "",
        "Rename the deepest directory to with name:",
        "  {mv_new_dir}",
        "",
        "The challenge is completed when:",
        "- the original directory name no longer exists",
        "- the renamed directory exists in the same parent directory",
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        parent_name, old_name, new_name = random.sample(DIR_NAMES, 3)

        parent_dir = ws / parent_name
        old_dir = parent_dir / old_name

        parent_dir.mkdir()
        old_dir.mkdir()

        # Persist expected paths
        state.mv_parent_dir = parent_name
        state.mv_old_dir = old_name
        state.mv_new_dir = new_name

        return state

    def evaluate(self, state: State, flag: str | None) -> bool:
        ws = Path(state.workspace)

        parent = ws / state.mv_parent_dir
        old_dir = parent / state.mv_old_dir
        new_dir = parent / state.mv_new_dir

        # Old directory must not exist
        if old_dir.exists():
            return False

        # New directory must exist
        if not new_dir.exists() or not new_dir.is_dir():
            return False

        return True

