from pathlib import Path
import random
from state import State

ECHO_FILENAME = "flag.txt"
ECHO_FLAGS = ["apple", "banana", "orange", "grape", "lemon"]

# ---------- REQUIRED PLUGIN SYMBOLS ----------

requires_flag_echo_redirect_two_words = False

title_echo_redirect_two_words = "Create a file using echo (two words)"

description_echo_redirect_two_words = [
    "Use the echo command with output redirection.",
    "Create a file named 'flag.txt' containing the text: \"{echo_words}\".",
    "The two words must be separated by exactly 3 (three) spaces.",
    "Hint: you will need quotes in the command line.",
    "The flag is the exact content of the file."
]

def setup_echo_redirect_two_words(state: State) -> State:
    # Choose two distinct random words
    w1, w2 = random.sample(ECHO_FLAGS, 2)
    words = f"{w1}   {w2}"

    # Persist visible data
    state.echo_words = words

    return state


def check_echo_redirect_two_words(state: State, flag: str | None) -> bool:
    ws = Path(state.workspace)
    target = ws / ECHO_FILENAME

    if not target.exists() or not target.is_file():
        return False

    try:
        content = target.read_text().strip()
    except Exception:
        return False

    # Accept both flag-less and explicit-flag submission
    if flag is None:
        return content == state.echo_words
    else:
        return content == state.echo_words and flag == content

