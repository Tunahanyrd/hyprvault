from pathlib import Path

from .utils import get_session_path, GREEN, RESET, YELLOW


def delete_session(name: str):
    session_path = get_session_path(name)
    if Path(session_path).exists():
        Path(session_path).unlink()
        print(f"{GREEN}[+]{RESET} Session deleted: {session_path}")
    else:
        print(f"{YELLOW}[!]{RESET} Session does not exist: {session_path}")
