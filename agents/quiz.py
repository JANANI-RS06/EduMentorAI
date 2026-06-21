"""
agents/quiz.py
--------------
Quiz & Interview Preparation Agent — generates MCQs, interview questions,
and detailed answers/explanations tailored to the student's goal and level.
"""

import os
import re
import json
import google.generativeai as genai


def _get_model() -> genai.GenerativeModel:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-2.5-flash")


# ---------------------------------------------------------------------------
# MCQ Generation
# ---------------------------------------------------------------------------

def generate_mcqs(goal: str, level: str, num_questions: int = 5) -> list[dict]:
    """
    Generate multiple-choice questions with explanations.

    Returns
    -------
    list of dicts, each with:
        'question'    : str
        'options'     : list[str]  — exactly 4 options (A–D)
        'answer'      : str        — e.g. 'A'
        'explanation' : str
    """
    model = _get_model()

    prompt = f"""
You are a professional quiz designer and educator.
Generate exactly {num_questions} multiple-choice questions about **{goal}**
at **{level}** difficulty level.

Return ONLY valid JSON — no markdown fences, no extra text — in this exact structure:

[
  {{
    "question": "Question text here?",
    "options": ["A. Option one", "B. Option two", "C. Option three", "D. Option four"],
    "answer": "A",
    "explanation": "Detailed explanation of why A is correct and why the others are wrong."
  }},
  ...
]

Rules:
- Questions must be factual and unambiguous.
- Options must be plausible distractors.
- Explanations must be educational (2–4 sentences).
- Vary question types: definition, application, comparison, scenario.
- Calibrate difficulty to {level} level.
- Return exactly {num_questions} questions.
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown fences if model adds them despite instructions
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    try:
        questions = json.loads(raw)
        # Basic schema validation
        for q in questions:
            assert "question" in q
            assert "options" in q and len(q["options"]) == 4
            assert "answer" in q
            assert "explanation" in q
        return questions
    except (json.JSONDecodeError, AssertionError, KeyError):
        # Fallback: return a single error entry so the UI doesn't crash
        return [{
            "question": "Could not parse MCQs. Please try again.",
            "options": ["A. N/A", "B. N/A", "C. N/A", "D. N/A"],
            "answer": "A",
            "explanation": f"Raw model output:\n{raw[:500]}",
        }]


# ---------------------------------------------------------------------------
# Interview Question Generation
# ---------------------------------------------------------------------------

def generate_interview_questions(goal: str, level: str, num_questions: int = 5) -> list[dict]:
    """
    Generate interview Q&A pairs with tips.

    Returns
    -------
    list of dicts, each with:
        'question'   : str
        'answer'     : str
        'tip'        : str  — interviewer insight / follow-up advice
        'category'   : str  — e.g. 'Conceptual', 'Practical', 'Behavioural'
    """
    model = _get_model()

    prompt = f"""
You are a senior technical interviewer and career coach.
Generate exactly {num_questions} interview questions for **{goal}**
targeting a **{level}** candidate.

Return ONLY valid JSON — no markdown fences, no extra text — in this structure:

[
  {{
    "question": "Interview question text?",
    "answer": "Comprehensive model answer (4–6 sentences). Include key points an interviewer looks for.",
    "tip": "Insider tip: what interviewers really want to hear, common mistakes to avoid, or follow-up questions to expect.",
    "category": "Conceptual | Practical | Behavioural | System Design | Problem Solving"
  }},
  ...
]

Rules:
- Mix categories: conceptual theory, practical coding/scenarios, and at least one behavioural question.
- Answers must be thorough but concise enough to deliver in 2 minutes.
- Tips should be genuinely useful career advice.
- Calibrate to {level} level.
- Return exactly {num_questions} questions.
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    try:
        questions = json.loads(raw)
        for q in questions:
            assert "question" in q
            assert "answer" in q
            assert "tip" in q
            assert "category" in q
        return questions
    except (json.JSONDecodeError, AssertionError, KeyError):
        return [{
            "question": "Could not parse interview questions. Please try again.",
            "answer": f"Raw output:\n{raw[:500]}",
            "tip": "Try regenerating.",
            "category": "Error",
        }]


# ---------------------------------------------------------------------------
# Quick Topic Explainer (bonus helper used by the UI)
# ---------------------------------------------------------------------------

def explain_topic(goal: str, topic: str, level: str) -> str:
    """
    Generate a clear, concise explanation of a specific topic within the goal.
    """
    model = _get_model()
    prompt = f"""
Explain the following topic clearly and concisely for a {level}-level student
studying {goal}:

**Topic: {topic}**

Structure your answer in markdown:
- **What it is** (1–2 sentences)
- **Why it matters** (1–2 sentences)
- **Simple analogy** (1 sentence)
- **Key things to remember** (3–4 bullet points)
- **Example** (a brief code snippet or real-world example if applicable)
"""
    return model.generate_content(prompt).text
