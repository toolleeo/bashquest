from pathlib import Path
import random
from state import State
from utils import hash_flag

ECHO_FILENAME = "flag.txt"
ECHO_FLAGS = ["apple", "banana", "orange", "grape", "lemon"]

# ---------- REQUIRED PLUGIN SYMBOLS ----------

title_echo_redirect_single_word = "Create a file using echo"

description_echo_redirect_single_word = [
    "Use the echo command with output redirection.",
    "Create a file named 'flag.txt' containing the word: {echo_word}.",
    "The flag is this single word."
]

def setup_echo_redirect_single_word(state: State) -> State:
    # Choose the word to be written
    word = random.choice(ECHO_FLAGS)

    # Persist visible data
    state.echo_word = word

    return state


def check_echo_redirect_single_word(state: State, flag: str) -> bool:
    ws = Path(state.workspace)
    target = ws / ECHO_FILENAME

    if not target.exists() or not target.is_file():
        return False

    try:
        content = target.read_text().strip()
    except Exception:
        return False

    return content == state.echo_word and flag == state.echo_word
