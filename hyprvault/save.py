import json
import subprocess
from dataclasses import dataclass, asdict
from typing import List
from pathlib import Path

from .utils import get_session_path, GREEN, RESET, YELLOW


@dataclass
class WindowState:
    command: str  # /proc/{pid}/cmdline
    class_name: str
    workspace_id: int
    is_floating: bool
    fullscreen: int
    focus_history_id: int
    at: List[int]
    size: List[int]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            command=data.get("command", ""),
            class_name=data.get("class", ""),
            workspace_id=data["workspace"]["id"],
            is_floating=data.get("floating", False),
            fullscreen=data.get("fullscreen", 0),
            focus_history_id=data.get("focusHistoryID", 999),
            at=data.get("at", [0, 0]),
            size=data.get("size", [0, 0]),
        )


def get_exec_command(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            cmd_bytes = f.read().split(bytes([0]))  # null-term
            cmd = cmd_bytes[0].decode("utf-8")
            return cmd if cmd else ""
    except Exception:
        return ""


def save_session(name="last_session"):
    try:
        output = subprocess.check_output(["hyprctl", "clients", "-j"], text=True)
        data = json.loads(output)
    except subprocess.CalledProcessError:
        return

    windows = []
    for w in data:
        if (
            w.get("mapped")
            and w.get("initialClass")
            and "hypr-vault" not in w.get("title", "").lower()
        ):  # not add self
            state = WindowState.from_dict(w)
            state.command = get_exec_command(w.get("pid", 0))

            windows.append(state)

    session_path = get_session_path(name)
    if Path(session_path).exists():
        print(f"{YELLOW}[!]{RESET} Session already exists: {session_path}")
        print(f"{YELLOW}[!]{RESET} Do you want to overwrite it? (y/n)", end=" ")
        if input().lower() != "y":
            print(f"{YELLOW}[!]{RESET} Cancelled.")
            return
    
    with open(session_path, "w", encoding="utf-8") as f:
        json.dump([asdict(w) for w in windows], f, indent=4)
    print(f"{GREEN}[+]{RESET} Session saved to: {session_path}")


if __name__ == "__main__":
    save_session()
