"""
agents/planner.py
-----------------
Study Planner Agent — generates personalised 7-day and 30-day study plans
using the Gemini API.
"""

import os
import google.generativeai as genai
from datetime import datetime


def _get_model() -> genai.GenerativeModel:
    """Configure and return the Gemini model."""
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-2.5-flash")


def generate_study_plan(goal: str, level: str, hours_per_day: float) -> dict:
    """
    Generate a structured 7-day and 30-day study plan.

    Parameters
    ----------
    goal          : What the student wants to learn.
    level         : 'Beginner' | 'Intermediate' | 'Advanced'
    hours_per_day : Daily study budget in hours.

    Returns
    -------
    dict with keys:
        'seven_day'   : str  — detailed week-by-week plan
        'thirty_day'  : str  — four-week overview
        'daily_goals' : str  — concise daily targets for week 1
        'generated_at': str  — ISO timestamp
    """
    model = _get_model()

    # ---- 7-day plan prompt -----------------------------------------------
    week_prompt = f"""
You are an expert educational curriculum designer.
Create a detailed, actionable 7-day study plan for a student with these details:

- **Learning Goal:** {goal}
- **Current Level:** {level}
- **Available Study Time:** {hours_per_day} hours per day

Format your response EXACTLY as follows (use markdown):

## 🗓️ 7-Day Study Plan: {goal}

### Overview
(2-3 sentences summarising the week's learning arc)

### Day 1 — [Topic Title]
**Focus:** ...
**Activities:**
- (specific task with duration, e.g., "Watch intro video on X — 30 min")
- ...
**Outcome:** What the student will be able to do after this day.

### Day 2 — [Topic Title]
... (same structure)

(Continue for all 7 days)

### Weekly Milestones
- ...

### Tips for Success
- ...

Be specific, practical, and calibrated to the student's level.
Each day's plan should fit within {hours_per_day} hours.
"""

    # ---- 30-day plan prompt ----------------------------------------------
    month_prompt = f"""
You are an expert educational curriculum designer.
Create a comprehensive 30-day (4-week) study roadmap for:

- **Learning Goal:** {goal}
- **Current Level:** {level}
- **Available Study Time:** {hours_per_day} hours per day

Format your response EXACTLY as follows (use markdown):

## 📅 30-Day Learning Roadmap: {goal}

### Learning Phases

#### Phase 1: Foundation (Week 1)
**Theme:** ...
**Key Topics:**
- Topic 1: brief description
- Topic 2: brief description
- ...
**Week 1 Goal:** (one measurable outcome)

#### Phase 2: Core Concepts (Week 2)
**Theme:** ...
**Key Topics:** ...
**Week 2 Goal:** ...

#### Phase 3: Applied Practice (Week 3)
**Theme:** ...
**Key Topics:** ...
**Week 3 Goal:** ...

#### Phase 4: Mastery & Projects (Week 4)
**Theme:** ...
**Key Topics:** ...
**Week 4 Goal:** ...

### 30-Day Milestones
| Milestone | Target Date | Success Criteria |
|-----------|-------------|-----------------|
| ... | Day X | ... |

### Progress Check-ins
(Suggest 4 self-assessment points across the month)

### Final Project Idea
(A mini-project the student can build/do to consolidate all learning)
"""

    # ---- Daily goals prompt (quick reference) ----------------------------
    daily_prompt = f"""
Create a compact daily goal card for Week 1 of studying {goal} at {level} level,
spending {hours_per_day} hours/day.

Format as a simple markdown table:

| Day | Main Topic | Primary Task | Time Budget |
|-----|-----------|--------------|-------------|
| 1   | ...       | ...          | {hours_per_day}h |
...

Keep each entry to one line. Be concrete and actionable.
"""

    week_response  = model.generate_content(week_prompt)
    month_response = model.generate_content(month_prompt)
    daily_response = model.generate_content(daily_prompt)

    return {
        "seven_day":    week_response.text,
        "thirty_day":   month_response.text,
        "daily_goals":  daily_response.text,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
