import shutil
import hashlib
from pathlib import Path

WORKSPACE_DIR = "workspace"

short_names = ["bin","lib","src","tmp","var","log","opt","dev","etc","run"]

def make_writable_recursive(p: Path):
    if not p.exists():
        return
    try:
        p.chmod(0o777)
    except Exception:
        pass
    if p.is_dir():
        for c in p.iterdir():
            make_writable_recursive(c)

def reset_workspace(ws: Path):
    if ws.exists():
        make_writable_recursive(ws)
        shutil.rmtree(ws)
    ws.mkdir(parents=True, exist_ok=True)

def hash_flag(s: str) -> bytes:
    return hashlib.sha256(s.encode()).digest()
