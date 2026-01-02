from challenges.base import BaseChallenge
import random
import string
from pathlib import Path
from state import State
from utils import hash_flag

TOTAL_FILES = 300
MIN_MATCHES = 0
MAX_MATCHES = 10

def random_name(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))

class LSWildcardsChallenge(BaseChallenge):
    id = "ls_wildcards_star"
    title = "List files using wildcards"
    requires_flag = True

    description = [
        "The workspace contains hundreds of text files.",
        "All files have names made of 4-8 lowercase letters and end with '.txt'.",
        "",
        "How many files contain the sequence:",
        "  {ls_pattern}",
        "",
        "Use wildcards with ls to find the answer.",
        "The flag is the number of matching files."
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        pattern = random_name(random.choice([2, 3]))
        self.pattern = pattern
        state.ls_pattern = pattern

        # Patch description
        for i, line in enumerate(self.description):
            if "{{PATTERN}}" in line:
                self.description[i] = line.replace("{{PATTERN}}", f"'{pattern}'")

        # Decide number of matches
        match_count = random.randint(MIN_MATCHES, MAX_MATCHES)

        filenames: set[str] = set()

        def make_matching_name() -> str:
            name_len = random.randint(4, 8)
            pos = random.randint(0, name_len - len(pattern))
            chars = list(random_name(name_len))
            chars[pos:pos + len(pattern)] = pattern
            return "".join(chars)

        def make_non_matching_name() -> str:
            while True:
                name = random_name(random.randint(4, 8))
                if pattern not in name:
                    return name

        # Generate matching files
        while len([n for n in filenames if pattern in n]) < match_count:
            filenames.add(make_matching_name())

        # Generate non-matching files
        while len(filenames) < TOTAL_FILES:
            filenames.add(make_non_matching_name())

        # Create files
        for name in filenames:
            (ws / f"{name}.txt").touch()

        # Persist correct answer
        state.flag_hash = hash_flag(str(match_count))

        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag.strip()) == state.flag_hash
