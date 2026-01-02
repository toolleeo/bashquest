# bashquest

bashquest is an interactive shell training environment in the spirit of "capture-the-flag" competitions.
It guides the user through a series of challenges designed to teach and test basic and intermediate shell skills.

For each challenge, bashquest generates items (files and directories) within a workspace directory, and prints the request for the challenge.
The user is required to perform the necessary operation to accomplish with the request.

## Features

- Step-by-step challenges using standard Unix commands (`ls`, `cat`, `echo`, `mkdir`, `rmdir`, etc.).
- Support for multiple, independent quests into dedicated workspaces.
- Persistent state that keeps track of passed challenges.
- Encrypted storage to prevent cheating (secret key can be changed to support installation as super users).
- Plugin-based architecture for easy addition of new challenges.
- Both capture-the-flag and "put-the-flag" style challenges.
- Currently ships with exercises about relative and absolute path, file manipulation, and command-line tricks.

Anti-cheating measures are not meant to be robust against skilled, motivated users (all the stuff is local, including the secret key for personal usage), but should be enough to discourage cheating from beginners.

## Installation and usage

Clone the repository:

```bash
git clone https://github.com/toolleeo/bashquest.git
cd bashquest
```

## Basic commands

Start a new quest with:

```
python bashquest.py start
```

Submit the flag of the current challenge:

```
python bashquest.py submit <flag>
```

The flag is not necessary in case of "put-the-flag" challenges. Just do "submit".

List the challenges:

```
python bashquest.py start
```

Move to another challenge:

```
python bashquest.py goto <number>
```


