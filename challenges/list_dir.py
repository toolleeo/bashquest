from challenges.base import BaseChallenge
import random
from pathlib import Path
from state import State
from utils import hash_flag

COUNTRY_NAMES = [
    # Europe
    "italy", "france", "germany", "spain", "portugal",
    "greece", "belgium", "netherlands", "sweden", "norway",
    "china", "japan", "india", "south_korea", "thailand",
    "egypt", "south_africa", "nigeria", "kenya", "morocco",
    "canada", "mexico", "cuba", "jamaica", "venezuela",
    "brazil", "argentina", "chile", "peru", "colombia"
]

class LsCountryChallenge(BaseChallenge):
    id = "list_dir"
    title = "Find file name"
    description = [
        "A file has been created in the workspace.",
        "The name of the file (without extension) is the flag."
    ]
    requires_flag = True

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        # Pick a random country
        country = random.choice(COUNTRY_NAMES)
        filename = f"{country}.txt"

        # Create the file in workspace
        file_path = ws / filename
        file_path.write_text("This file is used to test ls command.\n")

        # Save hash of the flag (country name)
        state.flag_hash = hash_flag(country)
        state.workspace = str(ws)
        state.current_flag_word = country  # store plain word if needed
        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag) == state.flag_hash

