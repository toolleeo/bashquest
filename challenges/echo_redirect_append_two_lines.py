from pathlib import Path
import random
from state import State

ECHO_FILENAME = "flag.txt"
ECHO_FLAGS = ["apple", "banana", "orange", "grape", "lemon"]

# ---------- REQUIRED PLUGIN SYMBOLS ----------

requires_flag_echo_redirect_append_two_lines = False

title_echo_redirect_append_two_lines = "Append to a file"

description_echo_redirect_append_two_lines = [
    "The file 'flag.txt' has been created in the workspace.",
    "It contains exactly one line:",
    "  {echo_word_1}",
    "",
    "Append a second line so that the file contains exactly two lines.",
    "The second line must be: {echo_word_2}",
    "The flag is the exact content of the file."
]

def setup_echo_redirect_append_two_lines(state: State) -> State:
    ws = Path(state.workspace).resolve()

    # Choose two distinct words
    w1, w2 = random.sample(ECHO_FLAGS, 2)
    state.echo_word_1 = w1
    state.echo_word_2 = w2
    state.echo_expected_content = f"{w1}\n{w2}"

    # Pre-create the file with the first line
    target = ws / ECHO_FILENAME
    target.write_text(w1 + "\n")

    # Update description to display the words
    for i, line in enumerate(description_echo_redirect_append_two_lines):
        if "{echo_word_1}" in line:
            description_echo_redirect_append_two_lines[i] = line.replace("{echo_word_1}", f"'{w1}'")
        if "{echo_word_2}" in line:
            description_echo_redirect_append_two_lines[i] = line.replace("{echo_word_2}", f"'{w2}'")

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
