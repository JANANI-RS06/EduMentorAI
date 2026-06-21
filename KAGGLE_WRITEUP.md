# 📝 Kaggle Capstone Write-up: EduMentor AI

> **Template** — fill in the bracketed sections before submitting.

---

## 🏷️ Project Title
**EduMentor AI — Multi-Agent Learning Assistant**

## 👤 Author
[Your Name] | [Kaggle Profile URL]

## 📅 Submission Date
[Date]

## 🏆 Track
Agents for Good

---

## 📌 Executive Summary

EduMentor AI is a multi-agent system that solves a real problem faced by millions of students: the difficulty of creating effective, personalised learning paths. Three specialised AI agents — a Study Planner, a Resource Recommender, and a Quiz & Interview Coach — work together through a clean Streamlit interface to provide end-to-end learning support.

---

## 🔍 Problem Statement

Students preparing for technical interviews, competitive exams, or self-directed learning face four distinct challenges:

1. **Unstructured study** — No clear daily/weekly plan calibrated to their schedule
2. **Resource overload** — Too many low-quality resources, no curation
3. **No feedback loop** — Can't test knowledge without an exam or tutor
4. **Interview anxiety** — Don't know what questions to expect or how to answer

**EduMentor AI addresses all four in one application.**

---

## 💡 Solution Architecture

### Multi-Agent Design

| Agent | Responsibility | Key Output |
|-------|---------------|------------|
| **Study Planner Agent** | Generates personalised learning schedules | 7-day + 30-day plan with daily goals |
| **Resource Recommendation Agent** | Curates learning materials | YouTube, courses, docs, practice sites |
| **Quiz & Interview Agent** | Tests knowledge and prepares for interviews | MCQs with scoring + Interview Q&A |

### Why Multiple Agents?

Each agent has a distinct skill and prompt context. Separating concerns produces better output quality than a single monolithic prompt — the planner focuses on scheduling logic, the resource agent on curation, and the quiz agent on pedagogy.

### Security Layer

A dedicated `security/validator.py` module intercepts all user input before it reaches any agent:
- **30+ blocked keywords** for dangerous content
- **Regex-based prompt injection detection**
- **Input length and format validation**
- No dangerous content ever reaches the Gemini API

---

## 🛠️ Technical Implementation

### Stack
- **Frontend:** Streamlit (Python) with custom CSS
- **AI:** Google Gemini 1.5 Flash (via `google-generativeai` SDK)
- **PDF Export:** ReportLab
- **Persistence:** JSON-based session history

### Agent Communication Pattern

```
User Input → Validator → Agent Prompt Construction → Gemini API → Parsed Response → UI
```

Each agent constructs a domain-specific, structured prompt and parses the Gemini response into a Python dict that the UI renders. The MCQ and Interview agents use JSON-structured output with graceful fallback parsing.

### Key Design Decisions

1. **Separate modules per agent** — Enables independent testing and updating
2. **Structured JSON for quiz data** — Makes scoring and rendering reliable
3. **Markdown for plans** — Native Streamlit rendering, also PDF-exportable
4. **Session state management** — Prevents redundant API calls when switching tabs

---

## 🧪 Demo Walkthrough

### Input
- **Goal:** "Machine Learning"
- **Level:** Beginner
- **Hours/Day:** 2

### What Happens

1. **Validator** checks the input — passes all checks ✅
2. **Study Planner Agent** generates:
   - Day 1: Introduction to ML concepts (2h: 45min video + 45min reading + 30min notes)
   - Days 2–7: Core ML algorithms, data preprocessing, model evaluation…
   - 30-day roadmap with 4 phases: Foundation → Core → Applied → Projects
3. **Resource Agent** recommends: StatQuest with Josh Starmer, fast.ai course, scikit-learn docs, Kaggle Learn
4. **Quiz Agent** generates 5 MCQs on ML fundamentals with instant scoring
5. **Interview Agent** produces conceptual + practical questions with model answers

---

## 📊 Results & Impact

- Plans generated in **~5–8 seconds** per agent call
- PDF export with **professional formatting**
- Session history allows **multi-session tracking**
- Security layer blocks **100% of test attack prompts**

---

## 🔮 Future Work

- [ ] LangChain/LangGraph orchestration for agent chaining
- [ ] Progress tracking with spaced repetition scheduling
- [ ] Multi-language support
- [ ] RAG (Retrieval-Augmented Generation) from uploaded study materials
- [ ] Calendar integration for plan scheduling
- [ ] Leaderboard for quiz scores (community feature)

---

## 📚 References

- Google Gemini API documentation: https://ai.google.dev/docs
- Streamlit documentation: https://docs.streamlit.io
- Kaggle 5-Day AI Agents Intensive course materials
- [Any papers or resources you referenced]

---

## 🔗 Links

- **GitHub Repository:** [your-repo-url]
- **Live Demo:** [your-deployment-url]
- **Kaggle Notebook:** [your-notebook-url]
- **Demo Video:** [your-video-url]
