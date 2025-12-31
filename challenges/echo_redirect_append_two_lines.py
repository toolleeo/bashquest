from pathlib import Path
import random
from state import State

ECHO_FILENAME = "flag.txt"
ECHO_FLAGS = ["apple", "banana", "orange", "grape", "lemon"]

# ---------- REQUIRED PLUGIN SYMBOLS ----------

requires_flag_echo_redirect_append_two_lines = False

title_echo_redirect_append_two_lines = "Append to a file"

description_echo_redirect_append_two_lines = [
    "Use two consecutive echo commands with output redirection.",
    "Create a file named 'flag.txt' containing exactly two lines.",
    "The first line must be: {echo_word_1}",
    "The second line must be: {echo_word_2}",
    "Hint: the second echo must append to the file.",
    "The flag is the exact content of the file."
]

def setup_echo_redirect_append_two_lines(state: State) -> State:
    # Choose two distinct words
    w1, w2 = random.sample(ECHO_FLAGS, 2)

    state.echo_word_1 = w1
    state.echo_word_2 = w2
    state.echo_expected_content = f"{w1}\n{w2}"

    return state


def check_echo_redirect_append_two_lines(state: State, flag: str | None) -> bool:
    ws = Path(state.workspace)
    target = ws / ECHO_FILENAME

    if not target.exists() or not target.is_file():
        return False

    try:
        content = target.read_text().rstrip("\n")
    except Exception:
        return False

    # Accept both flag-less and explicit-flag submission
    if flag is None:
        return content == state.echo_expected_content
    else:
        return content == state.echo_expected_content and flag == content

