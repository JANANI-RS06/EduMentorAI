@@ -1,80 +0,0 @@
"""
utils/history.py
----------------
Lightweight JSON-based history store for saving and loading user sessions.
All data is stored in a local `history/` directory as JSON files.
"""

import json
import os
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path("history")


def _ensure_dir() -> None:
    HISTORY_DIR.mkdir(exist_ok=True)


def save_session(goal: str, level: str, hours: float, plan: dict) -> str:
    """
    Persist a learning session to disk.

    Returns
    -------
    str — filename of the saved session (without path).
    """
    _ensure_dir()
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = goal.lower().replace(" ", "_")[:30]
    filename = f"{ts}_{slug}.json"

    payload = {
        "goal":         goal,
        "level":        level,
        "hours_per_day": hours,
        "plan":         plan,
        "saved_at":     datetime.utcnow().isoformat() + "Z",
    }

    with open(HISTORY_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return filename


def load_all_sessions() -> list[dict]:
    """
    Return all saved sessions, newest first.
    Each entry includes the filename for reference.
    """
    _ensure_dir()
    sessions = []
    for p in sorted(HISTORY_DIR.glob("*.json"), reverse=True):
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            data["_filename"] = p.name
            sessions.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return sessions


def load_session(filename: str) -> dict | None:
    """Load a single session by filename. Returns None if not found."""
    path = HISTORY_DIR / filename
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def delete_session(filename: str) -> bool:
    """Delete a session. Returns True if deleted, False if not found."""
    path = HISTORY_DIR / filename
    if path.exists():
        path.unlink()
        return True
    return False
