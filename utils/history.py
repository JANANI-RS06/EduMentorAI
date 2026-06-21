import json
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path("history")

def _ensure_dir():
HISTORY_DIR.mkdir(exist_ok=True)

def save_session(goal, level, hours, plan):
_ensure_dir()

```
ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
filename = f"{ts}.json"

payload = {
    "goal": goal,
    "level": level,
    "hours_per_day": hours,
    "plan": plan
}

with open(HISTORY_DIR / filename, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

return filename
```

def load_all_sessions():
_ensure_dir()

```
sessions = []

for p in HISTORY_DIR.glob("*.json"):
    try:
        with open(p, encoding="utf-8") as f:
            sessions.append(json.load(f))
    except Exception:
        pass

return sessions
```

def delete_session(filename):
path = HISTORY_DIR / filename

```
if path.exists():
    path.unlink()
    return True

return False
```
