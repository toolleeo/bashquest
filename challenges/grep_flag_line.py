from challenges.base import BaseChallenge
import random
import string
from pathlib import Path
from state import State
from utils import hash_flag

DATA_FILENAME = "data.txt"

VOCABULARY = [
    "apple", "banana", "orange", "grape", "lemon",
    "peach", "pear", "plum", "mango", "papaya",
    "kiwi", "melon", "cherry", "fig", "date",
    "apricot", "avocado", "coconut", "lime", "guava",
    "raspberry", "blueberry", "blackberry", "cranberry",
    "pineapple", "nectarine", "pomegranate", "tangerine",
    "watermelon", "passionfruit",
]

def random_text(min_len=2, max_len=15) -> str:
    length = random.randint(min_len, max_len)
    return "".join(random.choices(string.ascii_lowercase, k=length))


class GrepFlagLineChallenge(BaseChallenge):
    id = "grep_flag_line"
    title = "Search line in file"
    requires_flag = True

    description = [
        "A large text file named 'data.txt' has been created in the workspace.",
        "The file contains thousands of short lines of text.",
        "",
        "Exactly one line contains:",
        "  flag:WORD",
        "",
        "The flag is the word after 'flag:'."
        "Use grep to find the correct line.",
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()
        data_file = ws / DATA_FILENAME

        total_lines = random.randint(10_000, 20_000)

        # Choose the flag
        flag_word = random.choice(VOCABULARY)
        flag_line = f"flag:{flag_word}"

        lines: list[str] = []

        # Insert the real flag line at a random position
        flag_position = random.randint(0, total_lines - 1)

        for i in range(total_lines):
            if i == flag_position:
                lines.append(flag_line)
                continue

            # Generate decoy lines
            if random.random() < 0.3:
                # Line contains "flag" but NOT "flag:"
                prefix = random_text(1, 5)
                suffix = random_text(1, 5)
                decoy = f"{prefix}flag{suffix}"
                lines.append(decoy[:15])
            else:
                lines.append(random_text())

        data_file.write_text("\n".join(lines) + "\n")

        # Persist state
        state.flag_hash = hash_flag(flag_word)
        state.flag_word = flag_word

        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag.strip()) == state.flag_hash

