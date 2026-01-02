from challenges.base import BaseChallenge
import random
import string
from pathlib import Path
from state import State
from utils import hash_flag

NUM_FILES = 100
MIN_LINES_PER_FILE = 100
MAX_LINES_PER_FILE = 300

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


class GrepFlagAcrossFilesChallenge(BaseChallenge):
    id = "grep_flag_across_files"
    title = "Find a line across many files using grep"
    requires_flag = True

    description = [
        "The workspace contains many text files.",
        "Each file contains hundreds of short lines of text.",
        "",
        "Exactly one line across all files starts with:",
        "  flag:WORD",
        "",
        "The flag is the word after 'flag:'."
        "Use grep to find the correct line.",
    ]

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()

        # Choose the flag word
        flag_word = random.choice(VOCABULARY)
        flag_line = f"flag:{flag_word}"

        # Choose which file will contain the real flag
        flag_file_index = random.randint(0, NUM_FILES - 1)

        for i in range(NUM_FILES):
            filename = ws / f"data_{i:03d}.txt"
            lines: list[str] = []

            num_lines = random.randint(MIN_LINES_PER_FILE, MAX_LINES_PER_FILE)

            # Decide position of flag line (only in one file)
            flag_position = (
                random.randint(0, num_lines - 1)
                if i == flag_file_index
                else None
            )

            for line_idx in range(num_lines):
                if flag_position is not None and line_idx == flag_position:
                    lines.append(flag_line)
                    continue

                # Decoy lines
                if random.random() < 0.3:
                    prefix = random_text(1, 5)
                    suffix = random_text(1, 5)
                    decoy = f"{prefix}flag{suffix}"
                    lines.append(decoy[:15])
                else:
                    lines.append(random_text())

            filename.write_text("\n".join(lines) + "\n")

        # Persist state
        state.flag_hash = hash_flag(flag_word)
        state.grep_flag_word = flag_word

        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag.strip()) == state.flag_hash

