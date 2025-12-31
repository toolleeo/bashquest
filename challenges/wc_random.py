from challenges.base import BaseChallenge
import random
import string
from pathlib import Path
from state import State
from utils import hash_flag

NUM_WORDS_MIN = 50
NUM_WORDS_MAX = 500

class WordCountChallenge(BaseChallenge):
    id = "wc_random"
    title = "Count words in a file"
    description = [
        "A file has been created in the workspace with a random number of words.",
        "Words are sequences of characters separated by spaces."
        "Use the appropriate command to count the words in the file.",
        "The flag is the number of words in the file."
    ]
    requires_flag = True

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()
        ws.mkdir(parents=True, exist_ok=True)

        # Random file name
        fname = "".join(random.choices(string.ascii_lowercase, k=8)) + ".txt"
        file_path = ws / fname

        # Random number of words
        num_words = random.randint(NUM_WORDS_MIN, NUM_WORDS_MAX)
        words = ["".join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
                 for _ in range(num_words)]
        content = " ".join(words)

        file_path.write_text(content)

        state.wc_file_name = fname
        state.wc_word_count = num_words
        return state

    def evaluate(self, state: State, flag: str) -> bool:
        try:
            return int(flag) == getattr(state, "wc_word_count")
        except (ValueError, AttributeError):
            return False
