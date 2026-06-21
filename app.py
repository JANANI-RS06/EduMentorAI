"""
app.py
------
EduMentor AI — Multi-Agent Learning Assistant
Entry point for the Streamlit web application.

Run:  streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

# ---- Internal modules ----
from security.validator import validate_input, sanitize_string
from agents.planner     import generate_study_plan
from agents.resource    import get_resources
from agents.quiz        import generate_mcqs, generate_interview_questions, explain_topic
from utils.history      import save_session, load_all_sessions, delete_session
from utils.pdf_export   import export_plan_to_pdf

# ── Load environment variables (.env or system) ───────────────────────────
load_dotenv()

# ── Page configuration ────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduMentor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — clean indigo/violet palette ───────────────────────────────
st.markdown("""
<style>
/* ─── Google Fonts ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@600;700&display=swap');

/* ─── Root tokens ───────────────────────────────────────── */
:root {
    --primary:   #4F46E5;
    --secondary: #7C3AED;
    --accent:    #06B6D4;
    --success:   #10B981;
    --warning:   #F59E0B;
    --danger:    #EF4444;
    --bg:        #0F0E1A;
    --surface:   #1A1830;
    --surface2:  #252240;
    --border:    #2E2B50;
    --text:      #E8E6FF;
    --muted:     #9590C0;
}

/* ─── Global ────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* ─── Sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ─── Inputs ────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
[data-testid="stSlider"] .stSlider { accent-color: var(--primary); }

/* ─── Primary button ────────────────────────────────────── */
div.stButton > button[kind="primary"],
div.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.01em;
    transition: opacity 0.2s, transform 0.1s;
}
div.stButton > button:hover {
    opacity: 0.88;
    transform: translateY(-1px);
}

/* ─── Tabs ───────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tab"] {
    background: var(--surface2);
    border-radius: 8px 8px 0 0;
    color: var(--muted);
    font-weight: 500;
    padding: 0.5rem 1.2rem;
    border: 1px solid var(--border);
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: var(--primary);
    color: #fff;
    border-color: var(--primary);
}

/* ─── Cards ──────────────────────────────────────────────── */
.edu-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.edu-card-accent {
    border-left: 4px solid var(--accent);
}
.edu-card-primary {
    border-left: 4px solid var(--primary);
}
.edu-card-success {
    border-left: 4px solid var(--success);
}

/* ─── Hero banner ────────────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #1E1B4B 100%);
    border: 1px solid #3730A3;
    border-radius: 16px;
    padding: 2.4rem 2rem;
    text-align: center;
    margin-bottom: 1.6rem;
}
.hero-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #A5B4FC, #C4B5FD, #67E8F9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.15;
}
.hero-sub {
    color: #A5B4FC;
    font-size: 1.05rem;
    margin-top: 0.5rem;
    font-weight: 400;
}

/* ─── Agent badges ───────────────────────────────────────── */
.agent-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

/* ─── MCQ card ───────────────────────────────────────────── */
.mcq-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.mcq-question { font-weight: 600; font-size: 1rem; color: var(--text); }
.mcq-option   { color: var(--muted); padding: 0.2rem 0; }
.mcq-answer   { color: var(--success); font-weight: 600; }
.mcq-explain  { color: var(--accent); font-size: 0.9rem; margin-top: 0.5rem; }

/* ─── Expander ───────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
}

/* ─── Progress bar ───────────────────────────────────────── */
.stProgress > div > div { background: linear-gradient(90deg, var(--primary), var(--accent)); }

/* ─── Metric ─────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.8rem 1rem;
}

/* ─── Success / error / info boxes ──────────────────────── */
.stAlert { border-radius: 10px !important; }

/* ─── Markdown content area ──────────────────────────────── */
.plan-content {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.6rem;
}
</style>
""", unsafe_allow_html=True)


# ── Session-state defaults ─────────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "plan_result":       None,
        "resources_result":  None,
        "mcqs":              None,
        "interview_qs":      None,
        "quiz_score":        None,
        "selected_answers":  {},
        "quiz_submitted":    False,
        "active_session":    None,
        "explain_result":    None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ── Helpers ────────────────────────────────────────────────────────────────
def _check_api_key() -> bool:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key or key == "your_gemini_api_key_here":
        st.error(
            "🔑 **Gemini API key not found.**\n\n"
            "1. Copy `.env.example` → `.env`\n"
            "2. Add your key: `GEMINI_API_KEY=your_key_here`\n"
            "3. Restart the app.\n\n"
            "Get a free key at [aistudio.google.com](https://aistudio.google.com)."
        )
        return False
    return True


def _render_hero() -> None:
    st.markdown("""
    <div class="hero-banner">
        <p class="hero-title">🎓 EduMentor AI</p>
        <p class="hero-sub">
            Your personal multi-agent learning assistant — powered by Google Gemini
        </p>
    </div>
    """, unsafe_allow_html=True)


def _agent_label(text: str) -> None:
    st.markdown(f'<span class="agent-badge">🤖 {text}</span>', unsafe_allow_html=True)


# ── Sidebar — input form ───────────────────────────────────────────────────
def _render_sidebar() -> tuple[str, str, float]:
    with st.sidebar:
        st.markdown("## ⚙️ Configure Your Plan")
        st.markdown("---")

        goal = st.text_input(
            "🎯 Learning Goal",
            placeholder="e.g. Machine Learning, DSA, UPSC, Japanese N5…",
            help="What do you want to master? Be specific for better plans.",
        )

        level = st.selectbox(
            "📊 Skill Level",
            ["Beginner", "Intermediate", "Advanced"],
            help="Your current knowledge level in this topic.",
        )

        hours = st.slider(
            "⏱️ Study Hours / Day",
            min_value=0.5,
            max_value=12.0,
            value=2.0,
            step=0.5,
            format="%.1f h",
            help="How many hours can you realistically study each day?",
        )

        st.markdown("---")
        generate_btn = st.button("🚀 Generate Learning Plan", use_container_width=True)

        # Stats
        st.markdown("---")
        st.markdown("### 📈 Session Stats")
        sessions = load_all_sessions()
        col1, col2 = st.columns(2)
        col1.metric("Plans Saved", len(sessions))
        col2.metric("Hours/Day", f"{hours}h")

        # History in sidebar
        if sessions:
            st.markdown("---")
            st.markdown("### 🕐 Recent Plans")
            for s in sessions[:5]:
                with st.expander(f"📘 {s['goal'][:25]}…" if len(s['goal']) > 25 else f"📘 {s['goal']}"):
                    st.caption(f"Level: {s['level']} | {s['hours_per_day']}h/day")
                    if st.button("Load", key=f"load_{s['_filename']}"):
                        st.session_state.plan_result = s.get("plan")
                        st.session_state.active_session = s
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"del_{s['_filename']}"):
                        delete_session(s["_filename"])
                        st.rerun()

    return goal, level, hours, generate_btn


# ── Tab 1: Study Plan ──────────────────────────────────────────────────────
def _tab_plan(goal: str, level: str, hours: float) -> None:
    _agent_label("Study Planner Agent")
    st.markdown("### 📅 Your Personalised Study Plan")

    plan = st.session_state.plan_result

    if plan is None:
        st.info("👈 Fill in the sidebar and click **Generate Learning Plan** to start.")
        return

    # Quick-reference daily table
    with st.expander("⚡ Week 1 — Daily Goals at a Glance", expanded=True):
        st.markdown(plan["daily_goals"])

    # Tabs within tabs
    inner_tabs = st.tabs(["📆 7-Day Plan", "📅 30-Day Roadmap"])

    with inner_tabs[0]:
        st.markdown(
            f'<div class="plan-content">{plan["seven_day"]}</div>',
            unsafe_allow_html=True,
        )

    with inner_tabs[1]:
        st.markdown(
            f'<div class="plan-content">{plan["thirty_day"]}</div>',
            unsafe_allow_html=True,
        )

    # Export buttons
    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        try:
            pdf_bytes = export_plan_to_pdf(
                goal, level, hours,
                plan["seven_day"], plan["thirty_day"], plan["daily_goals"],
            )
            st.download_button(
                "📥 Download PDF",
                data=pdf_bytes,
                file_name=f"EduMentor_{goal.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.warning(f"PDF export unavailable: {e}")

    with col_b:
        plan_text = f"# EduMentor AI — {goal}\n\n{plan['seven_day']}\n\n{plan['thirty_day']}"
        st.download_button(
            "📝 Download Markdown",
            data=plan_text,
            file_name=f"EduMentor_{goal.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col_c:
        if st.button("💾 Save to History", use_container_width=True):
            fname = save_session(goal, level, hours, plan)
            st.success(f"✅ Saved as `{fname}`")


# ── Tab 2: Resources ───────────────────────────────────────────────────────
def _tab_resources(goal: str, level: str) -> None:
    _agent_label("Resource Recommendation Agent")
    st.markdown("### 🌐 Curated Learning Resources")

    if st.session_state.resources_result is None:
        if st.session_state.plan_result is None:
            st.info("👈 Generate a learning plan first, then come back here.")
            return
        if st.button("🔍 Fetch Resources for My Goal"):
            with st.spinner("🔍 Searching for the best resources…"):
                try:
                    st.session_state.resources_result = get_resources(goal, level)
                except Exception as e:
                    st.error(f"Resource fetch failed: {e}")
                    return

    res = st.session_state.resources_result
    if res is None:
        return

    tabs = st.tabs(["📺 YouTube", "🎓 Courses", "🌐 Websites & Docs", "🛠️ Practice"])

    with tabs[0]:
        st.markdown(res["youtube"])
    with tabs[1]:
        st.markdown(res["courses"])
    with tabs[2]:
        st.markdown(res["websites"])
    with tabs[3]:
        st.markdown(res["practice"])


# ── Tab 3: Quiz ────────────────────────────────────────────────────────────
def _tab_quiz(goal: str, level: str) -> None:
    _agent_label("Quiz & Interview Agent — MCQ Mode")
    st.markdown("### 🧠 Test Your Knowledge")

    if st.session_state.plan_result is None:
        st.info("👈 Generate a learning plan first.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        num_q = st.slider("Number of questions", 3, 10, 5)
    with col2:
        gen_btn = st.button("🎲 Generate Quiz", use_container_width=True)

    if gen_btn:
        with st.spinner("🧠 Crafting your quiz…"):
            try:
                st.session_state.mcqs            = generate_mcqs(goal, level, num_q)
                st.session_state.selected_answers = {}
                st.session_state.quiz_submitted   = False
                st.session_state.quiz_score       = None
            except Exception as e:
                st.error(f"Quiz generation failed: {e}")
                return

    mcqs = st.session_state.mcqs
    if not mcqs:
        return

    # Render questions
    with st.form("quiz_form"):
        for i, q in enumerate(mcqs):
            st.markdown(f"""
            <div class="mcq-card">
                <p class="mcq-question">Q{i+1}. {q['question']}</p>
            </div>
            """, unsafe_allow_html=True)

            option_labels = [opt.split(". ", 1)[-1] if ". " in opt else opt for opt in q["options"]]
            answer_keys   = [opt[0] for opt in q["options"]]  # A, B, C, D

            selected = st.radio(
                f"Select answer for Q{i+1}:",
                options=answer_keys,
                format_func=lambda k, opts=q["options"]: next(
                    (o for o in opts if o.startswith(k)), k
                ),
                key=f"mcq_{i}",
                label_visibility="collapsed",
            )
            st.session_state.selected_answers[i] = selected
            st.markdown("---")

        submitted = st.form_submit_button("✅ Submit Quiz", use_container_width=True)

    if submitted:
        st.session_state.quiz_submitted = True
        correct = sum(
            1 for i, q in enumerate(mcqs)
            if st.session_state.selected_answers.get(i) == q["answer"]
        )
        st.session_state.quiz_score = (correct, len(mcqs))

    if st.session_state.quiz_submitted and st.session_state.quiz_score:
        correct, total = st.session_state.quiz_score
        pct = correct / total
        colour = "success" if pct >= 0.7 else "warning" if pct >= 0.4 else "danger"

        st.markdown(f"### 🏆 Score: {correct}/{total} ({pct*100:.0f}%)")
        st.progress(pct)

        if pct == 1.0:
            st.success("🎉 Perfect score! You're mastering this topic!")
        elif pct >= 0.7:
            st.success("✅ Great job! Keep practising to solidify your knowledge.")
        elif pct >= 0.4:
            st.warning("📚 Good effort! Review the explanations below.")
        else:
            st.error("💡 Keep studying — check the explanations and try again.")

        st.markdown("### 📖 Explanations")
        for i, q in enumerate(mcqs):
            user_ans    = st.session_state.selected_answers.get(i, "?")
            correct_ans = q["answer"]
            is_right    = user_ans == correct_ans
            icon        = "✅" if is_right else "❌"

            with st.expander(f"{icon} Q{i+1}: {q['question'][:80]}…"):
                st.markdown(f"**Your answer:** {user_ans} | **Correct:** {correct_ans}")
                st.markdown(f"_{q['explanation']}_")


# ── Tab 4: Interview Prep ─────────────────────────────────────────────────
def _tab_interview(goal: str, level: str) -> None:
    _agent_label("Quiz & Interview Agent — Interview Mode")
    st.markdown("### 💼 Interview Preparation")

    if st.session_state.plan_result is None:
        st.info("👈 Generate a learning plan first.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        num_q = st.slider("Number of interview questions", 3, 10, 5, key="interview_num")
    with col2:
        gen_btn = st.button("🎤 Generate Questions", use_container_width=True)

    if gen_btn:
        with st.spinner("🤝 Preparing interview questions…"):
            try:
                st.session_state.interview_qs = generate_interview_questions(goal, level, num_q)
            except Exception as e:
                st.error(f"Interview generation failed: {e}")
                return

    qs = st.session_state.interview_qs
    if not qs:
        return

    # Category filter
    categories = list({q["category"] for q in qs})
    selected_cats = st.multiselect(
        "Filter by category",
        options=categories,
        default=categories,
    )

    for i, q in enumerate([q for q in qs if q["category"] in selected_cats]):
        cat_colours = {
            "Conceptual": "🔵", "Practical": "🟢", "Behavioural": "🟡",
            "System Design": "🟣", "Problem Solving": "🟠",
        }
        icon = cat_colours.get(q["category"], "⚪")

        with st.expander(f"{icon} Q{i+1} [{q['category']}]: {q['question'][:80]}…"):
            st.markdown(f"**Question:** {q['question']}")
            st.markdown("---")
            st.markdown("**✅ Model Answer:**")
            st.markdown(q["answer"])
            st.markdown("---")
            st.markdown(f"**💡 Interviewer Tip:** _{q['tip']}_")

    # Topic explainer bonus feature
    st.markdown("---")
    st.markdown("### 🔍 Quick Topic Explainer")
    topic_input = st.text_input(
        "Enter a specific topic or concept to explain:",
        placeholder=f"e.g. 'backpropagation' in {goal}",
    )
    if st.button("Explain This Topic") and topic_input:
        with st.spinner("🧐 Generating explanation…"):
            try:
                explanation = explain_topic(goal, topic_input, level)
                st.session_state.explain_result = explanation
            except Exception as e:
                st.error(f"Explanation failed: {e}")

    if st.session_state.explain_result:
        st.markdown(
            f'<div class="edu-card edu-card-accent">{st.session_state.explain_result}</div>',
            unsafe_allow_html=True,
        )


# ── Tab 5: Progress Dashboard ─────────────────────────────────────────────
def _tab_progress() -> None:
    st.markdown("### 📊 Learning Progress Dashboard")

    sessions = load_all_sessions()
    if not sessions:
        st.info("No learning sessions saved yet. Generate and save a plan to track progress!")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📚 Plans Created", len(sessions))
    col2.metric(
        "⏱️ Total Study Hours/Week",
        f"{sum(s['hours_per_day'] * 7 for s in sessions):.0f}h",
    )

    goals = [s["goal"] for s in sessions]
    most_recent = sessions[0]["goal"] if sessions else "—"
    col3.metric("🎯 Latest Goal", most_recent[:15] + "…" if len(most_recent) > 15 else most_recent)

    levels = [s["level"] for s in sessions]
    col4.metric("📈 Most Common Level", max(set(levels), key=levels.count))

    # Goals table
    st.markdown("---")
    st.markdown("#### 📋 All Learning Sessions")

    for s in sessions:
        with st.expander(f"🎯 {s['goal']} — {s['level']} — {s['hours_per_day']}h/day"):
            st.caption(f"Saved: {s.get('saved_at', 'Unknown')}")
            if s.get("plan"):
                st.markdown("**7-Day Plan Preview:**")
                lines = s["plan"]["seven_day"].splitlines()[:10]
                st.markdown("\n".join(lines) + "\n…")
            col_a, col_b = st.columns(2)
            with col_b:
                if st.button("🗑️ Delete", key=f"del_prog_{s['_filename']}"):
                    delete_session(s["_filename"])
                    st.rerun()

    # Quiz score history
    if st.session_state.quiz_score:
        st.markdown("---")
        st.markdown("#### 🏆 Latest Quiz Result")
        correct, total = st.session_state.quiz_score
        st.metric("Score", f"{correct}/{total}", f"{correct/total*100:.0f}%")
        st.progress(correct / total)


# ── Main layout ────────────────────────────────────────────────────────────
def main() -> None:
    _render_hero()

    if not _check_api_key():
        st.stop()

    goal, level, hours, generate_btn = _render_sidebar()

    # Handle generation
    if generate_btn:
        is_valid, error_msg = validate_input(goal, hours, level)
        if not is_valid:
            st.error(error_msg)
            st.stop()

        goal_clean = sanitize_string(goal)

        with st.spinner("🤖 Study Planner Agent is crafting your personalised plan…"):
            try:
                plan = generate_study_plan(goal_clean, level, hours)
                st.session_state.plan_result      = plan
                st.session_state.resources_result = None   # reset stale data
                st.session_state.mcqs             = None
                st.session_state.interview_qs     = None
                st.session_state.quiz_score       = None
                st.session_state.quiz_submitted   = False
                st.session_state.selected_answers = {}
                st.success("✅ Your learning plan is ready! Explore the tabs below.")
            except Exception as e:
                st.error(f"🚨 Failed to generate plan: {e}")
                st.stop()

    # ── Main content tabs ─────────────────────────────────────────────────
    tabs = st.tabs([
        "📅 Study Plan",
        "🌐 Resources",
        "🧠 Quiz",
        "💼 Interview Prep",
        "📊 Progress",
    ])

    goal_display = st.session_state.active_session["goal"] \
        if st.session_state.active_session and st.session_state.plan_result \
        else (sanitize_string(goal) if goal else "")

    level_display = st.session_state.active_session["level"] \
        if st.session_state.active_session and st.session_state.plan_result \
        else level

    hours_display = st.session_state.active_session["hours_per_day"] \
        if st.session_state.active_session and st.session_state.plan_result \
        else hours

    with tabs[0]:
        _tab_plan(goal_display, level_display, hours_display)
    with tabs[1]:
        _tab_resources(goal_display, level_display)
    with tabs[2]:
        _tab_quiz(goal_display, level_display)
    with tabs[3]:
        _tab_interview(goal_display, level_display)
    with tabs[4]:
        _tab_progress()


if __name__ == "__main__":
    main()
