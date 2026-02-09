"""HyprVault utility functions and constants."""

import os
from pathlib import Path

# Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_config_dir() -> Path:
    """Get XDG-compliant config directory for hyprvault."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    config_dir = Path(xdg_config) / "hyprvault" / "sessions"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_session_path(name: str) -> Path:
    """Get the full path for a session file, handling .json extension."""
    # Strip .json if user provided it
    if name.endswith(".json"):
        name = name[:-5]

    return get_config_dir() / f"{name}.json"


def list_sessions() -> list[str]:
    """List all saved session names."""
    config_dir = get_config_dir()
    sessions = []
    for f in config_dir.glob("*.json"):
        sessions.append(f.stem)
    return sorted(sessions)
