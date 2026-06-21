"""
agents/resource.py
------------------
Resource Recommendation Agent — recommends YouTube channels, online courses,
websites, documentation, and practice platforms for any learning goal.
"""

import os
import google.generativeai as genai


def _get_model() -> genai.GenerativeModel:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-2.5-flash")


def get_resources(goal: str, level: str) -> dict:
    """
    Fetch curated resource recommendations for the given learning goal.

    Parameters
    ----------
    goal  : Learning topic (e.g., 'Machine Learning', 'Japanese N5').
    level : 'Beginner' | 'Intermediate' | 'Advanced'

    Returns
    -------
    dict with keys:
        'youtube'   : str  — YouTube channels & playlists
        'courses'   : str  — Online courses (free & paid)
        'websites'  : str  — Reference sites & docs
        'practice'  : str  — Hands-on practice resources
    """
    model = _get_model()

    # ---- YouTube channels ------------------------------------------------
    yt_prompt = f"""
You are an expert educational resource curator.
Recommend the BEST YouTube channels and specific playlists for learning:
**{goal}** at **{level}** level.

Format your response in markdown:

## 📺 YouTube Channels & Playlists

### Top Channels
For each channel, provide:
- **Channel Name** — [URL or search query]
  - Why it's great: (one sentence)
  - Best playlist/series: "Playlist Name"
  - Difficulty: {level}

List 5–7 channels, ordered from most beginner-friendly to advanced.
Be specific with real, well-known channels. Do not invent channels.
"""

    # ---- Courses ---------------------------------------------------------
    courses_prompt = f"""
You are an expert educational resource curator.
Recommend the BEST online courses for learning **{goal}** at **{level}** level.

Format in markdown:

## 🎓 Recommended Courses

### Free Courses
For each course:
- **Course Title** — Platform (e.g., Coursera, edX, freeCodeCamp)
  - Duration: X weeks / X hours
  - URL or search phrase
  - Why recommended: (one sentence)

### Paid Courses (Best Value)
(same structure)

### Certifications Worth Considering
(List 2–3 if applicable)

List 4–5 free and 3–4 paid courses. Be specific and accurate.
"""

    # ---- Websites & docs -------------------------------------------------
    web_prompt = f"""
You are an expert educational resource curator.
Recommend the BEST websites, documentation, and reading materials for:
**{goal}** at **{level}** level.

Format in markdown:

## 🌐 Websites & Documentation

### Official Documentation / References
- **Site Name** — URL
  - What it covers: ...

### Tutorials & Guides
- **Site Name** — URL
  - Best for: ...

### Communities & Forums
- **Community** — URL
  - Why join: ...

### Books (Optional but Valuable)
- **Title** by Author — free PDF / purchase link if available

Be specific with real URLs where possible. List 3–4 per sub-section.
"""

    # ---- Practice resources ----------------------------------------------
    practice_prompt = f"""
You are an expert educational resource curator.
Recommend hands-on PRACTICE resources for **{goal}** at **{level}** level.

Format in markdown:

## 🛠️ Practice & Hands-on Resources

### Coding / Problem-solving Platforms
(if applicable)
- **Platform** — URL
  - What to practice: ...
  - Recommended track/path: ...

### Projects to Build
List 3–5 project ideas at {level} level:
1. **Project Name** — brief description (skills practised)
2. ...

### Datasets / Open Resources
(if applicable)
- **Resource** — URL
  - Use case: ...

### Mock Exams / Quizzes
- **Resource** — URL
  - Type: ...

Tailor everything specifically to {goal}.
"""

    yt_resp       = model.generate_content(yt_prompt)
    courses_resp  = model.generate_content(courses_prompt)
    web_resp      = model.generate_content(web_prompt)
    practice_resp = model.generate_content(practice_prompt)

    return {
        "youtube":  yt_resp.text,
        "courses":  courses_resp.text,
        "websites": web_resp.text,
        "practice": practice_resp.text,
    }
