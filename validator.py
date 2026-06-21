"""
security/validator.py
---------------------
Input validation and prompt injection / dangerous content filtering.
All user-supplied strings pass through this module before reaching any agent.
"""

import re
from typing import Tuple

# ---------------------------------------------------------------------------
# Blocklists
# ---------------------------------------------------------------------------

# Terms that signal an attempt to misuse the system for harmful purposes
DANGEROUS_KEYWORDS: list[str] = [
    "hack", "hacking", "hacker",
    "malware", "ransomware", "spyware", "adware", "trojan",
    "exploit", "exploiting", "exploitation",
    "password cracking", "brute force", "credential stuffing",
    "phishing", "social engineering", "spear phishing",
    "sql injection", "xss", "cross-site scripting",
    "ddos", "denial of service",
    "keylogger", "rootkit", "backdoor",
    "bypass authentication", "privilege escalation",
    "zero day", "zero-day",
    "penetration testing without permission",
    "crack software", "software piracy", "warez",
    "darkweb", "dark web", "tor hidden service",
    "bomb", "weapon", "explosive",
    "drug synthesis", "drug manufacturing",
    "illegal", "criminal activity",
    "ignore previous", "ignore all instructions",
    "jailbreak", "dan mode", "developer mode override",
    "act as", "pretend you are", "you are now",
]

# Prompt-injection style patterns (regex)
INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?previous",
    r"forget\s+(all\s+)?previous",
    r"you\s+are\s+now\s+\w+",
    r"pretend\s+(to\s+be|you\s+are)",
    r"act\s+as\s+(if\s+you\s+are|a|an)\s+",
    r"(new|override)\s+system\s+prompt",
    r"print\s+(your\s+)?(system\s+)?prompt",
    r"reveal\s+(your\s+)?(instructions|prompt|system)",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_input(goal: str, hours: float, level: str) -> Tuple[bool, str]:
    """
    Validate all user inputs before they reach any agent.

    Parameters
    ----------
    goal  : Learning goal string supplied by the user.
    hours : Study hours per day.
    level : Skill level string.

    Returns
    -------
    (is_valid, error_message)
    """
    # --- Goal checks ---
    if not goal or not goal.strip():
        return False, "⚠️ Learning goal cannot be empty. Please describe what you want to learn."

    goal_stripped = goal.strip()

    if len(goal_stripped) < 3:
        return False, "⚠️ Learning goal is too short. Please be more descriptive (e.g., 'Machine Learning', 'DSA for interviews')."

    if len(goal_stripped) > 500:
        return False, "⚠️ Learning goal is too long (max 500 characters). Please be concise."

    # --- Dangerous content check ---
    is_safe, reason = _is_safe_content(goal_stripped)
    if not is_safe:
        return False, f"🚫 Blocked: {reason}\n\nEduMentor AI is designed exclusively for educational learning assistance."

    # --- Hours checks ---
    if hours is None:
        return False, "⚠️ Please specify your available study hours per day."

    if not (0.5 <= hours <= 16):
        return False, "⚠️ Study hours must be between 0.5 and 16 hours per day."

    # --- Level checks ---
    valid_levels = {"Beginner", "Intermediate", "Advanced"}
    if level not in valid_levels:
        return False, f"⚠️ Skill level must be one of: {', '.join(valid_levels)}."

    return True, ""


def sanitize_string(text: str) -> str:
    """
    Strip leading/trailing whitespace and collapse internal whitespace runs.
    Does NOT mutate dangerous content — call validate_input first.
    """
    return re.sub(r"\s+", " ", text.strip())


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_safe_content(text: str) -> Tuple[bool, str]:
    """Return (True, '') if safe, else (False, reason)."""
    lower = text.lower()

    # Keyword blocklist
    for kw in DANGEROUS_KEYWORDS:
        if kw in lower:
            return False, (
                f"Your input contains a restricted term: '{kw}'. "
                "Please keep queries focused on legitimate learning topics."
            )

    # Regex injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower):
            return False, (
                "Your input appears to contain a prompt-injection attempt. "
                "Please enter a genuine learning goal."
            )

    return True, ""
