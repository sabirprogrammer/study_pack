import os
import streamlit as st

from utils import read_uploaded_file, combine_source_text
from workflow import execute_workflow, MODEL_NAME


st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


defaults = {
    "topic": "",
    "learning_goal": "",
    "notes": "",
    "level": "Beginner",
    "study_time": "2 hours",
    "quiz_count": 10,
    "study_mode": "Exam Preparation",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def apply_preset(topic, goal, level, study_time, quiz_count, study_mode):
    st.session_state.topic = topic
    st.session_state.learning_goal = goal
    st.session_state.level = level
    st.session_state.study_time = study_time
    st.session_state.quiz_count = quiz_count
    st.session_state.study_mode = study_mode


st.markdown(
    """
<style>
:root {
    --primary: #7c3aed;
    --primary-2: #8b5cf6;
    --cyan: #06b6d4;
    --green: #22c55e;
    --amber: #f59e0b;
    --border: rgba(148, 163, 184, 0.17);
    --glass: rgba(255, 255, 255, 0.035);
    --muted: rgba(226, 232, 240, 0.67);
}
.block-container {
    max-width: 1240px;
    padding-top: 1.45rem;
    padding-bottom: 3.5rem;
}
[data-testid="stSidebar"] {
    border-right: 1px solid var(--border);
    background:
        radial-gradient(circle at 15% 5%, rgba(124, 58, 237, .16), transparent 26%),
        radial-gradient(circle at 90% 96%, rgba(6, 182, 212, .10), transparent 24%);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
.hero {
    position: relative;
    overflow: hidden;
    padding: 2.25rem 2.25rem 2rem;
    border: 1px solid var(--border);
    border-radius: 28px;
    background:
        radial-gradient(circle at 88% 15%, rgba(124,58,237,.24), transparent 28%),
        radial-gradient(circle at 7% 100%, rgba(6,182,212,.17), transparent 30%),
        linear-gradient(135deg, rgba(255,255,255,.055), rgba(255,255,255,.012));
    box-shadow: 0 20px 60px rgba(0,0,0,.14);
    margin-bottom: 1.25rem;
}
.hero:before {
    content: "";
    position: absolute;
    width: 260px;
    height: 260px;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 50%;
    right: -115px;
    top: -120px;
}
.hero:after {
    content: "";
    position: absolute;
    width: 135px;
    height: 135px;
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 50%;
    right: -25px;
    top: -15px;
}
.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    padding: .4rem .72rem;
    border-radius: 999px;
    border: 1px solid rgba(139,92,246,.28);
    background: rgba(139,92,246,.10);
    font-size: .76rem;
    font-weight: 750;
    letter-spacing: .02em;
    margin-bottom: .85rem;
}
.hero h1 {
    margin: 0;
    max-width: 800px;
    font-size: clamp(2.15rem, 5vw, 3.45rem);
    line-height: 1.02;
    letter-spacing: -.055em;
}
.hero p {
    max-width: 790px;
    margin: .85rem 0 0;
    font-size: 1.03rem;
    line-height: 1.7;
    opacity: .74;
}
.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    margin-top: 1.15rem;
}
.hero-pill {
    padding: .4rem .68rem;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,.028);
    font-size: .78rem;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: .8rem;
    margin: 1rem 0 1.25rem;
}
.stat-card {
    padding: .92rem 1rem;
    border-radius: 18px;
    border: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(255,255,255,.036), rgba(255,255,255,.014));
}
.stat-label {
    font-size: .68rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    opacity: .5;
}
.stat-value {
    margin-top: .24rem;
    font-size: .98rem;
    font-weight: 780;
}
.section-head {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 1rem;
    margin: .55rem 0 .85rem;
}
.section-title {
    font-size: 1.18rem;
    font-weight: 800;
    letter-spacing: -.02em;
}
.section-copy {
    margin-top: .2rem;
    opacity: .58;
    font-size: .82rem;
}
.glass-card {
    border: 1px solid var(--border);
    border-radius: 22px;
    background: linear-gradient(180deg, rgba(255,255,255,.035), rgba(255,255,255,.013));
    box-shadow: 0 12px 35px rgba(0,0,0,.08);
}
.card-pad { padding: 1rem 1.08rem; }
.sidebar-brand {
    padding: 1rem 1.05rem;
    border-radius: 19px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,.025);
    margin-bottom: 1rem;
}
.sidebar-title { font-size: 1.02rem; font-weight: 800; }
.sidebar-copy {
    margin-top: .2rem;
    opacity: .58;
    font-size: .77rem;
    line-height: 1.45;
}
.model-box {
    margin-top: .9rem;
    padding: .72rem .8rem;
    border-radius: 14px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,.018);
}
.model-label {
    font-size: .62rem;
    text-transform: uppercase;
    letter-spacing: .09em;
    opacity: .48;
}
.model-name {
    margin-top: .22rem;
    font-family: monospace;
    font-size: .77rem;
    opacity: .82;
    overflow-wrap: anywhere;
}
.workflow-grid { display: grid; gap: .64rem; }
.flow-item {
    display: grid;
    grid-template-columns: 40px 1fr;
    gap: .72rem;
    align-items: center;
    padding: .75rem;
    border-radius: 15px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,.02);
    transition: transform .15s ease, border-color .15s ease;
}
.flow-item:hover {
    transform: translateY(-1px);
    border-color: rgba(139,92,246,.34);
}
.flow-icon {
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: linear-gradient(145deg, rgba(139,92,246,.16), rgba(6,182,212,.08));
    border: 1px solid rgba(139,92,246,.18);
}
.flow-title { font-size: .89rem; font-weight: 750; }
.flow-copy {
    margin-top: .08rem;
    font-size: .74rem;
    opacity: .56;
    line-height: 1.4;
}
.feature-card {
    min-height: 132px;
    padding: 1rem 1.05rem;
    border: 1px solid var(--border);
    border-radius: 19px;
    background: rgba(255,255,255,.02);
}
.feature-icon { font-size: 1.25rem; margin-bottom: .42rem; }
.feature-title { font-size: .9rem; font-weight: 780; }
.feature-copy {
    font-size: .75rem;
    line-height: 1.48;
    opacity: .57;
    margin-top: .2rem;
}
.stage-card {
    padding: .9rem .5rem;
    border-radius: 17px;
    border: 1px solid var(--border);
    text-align: center;
    background: linear-gradient(180deg, rgba(255,255,255,.032), rgba(255,255,255,.012));
}
.stage-icon { font-size: 1.18rem; }
.stage-label {
    font-size: .84rem;
    font-weight: 760;
    margin-top: .22rem;
}
.stage-status {
    font-size: .7rem;
    opacity: .55;
    margin-top: .1rem;
}
.result-banner {
    padding: 1rem 1.1rem;
    border: 1px solid rgba(34,197,94,.22);
    background: rgba(34,197,94,.06);
    border-radius: 18px;
    margin-bottom: .8rem;
}
.result-title { font-size: .95rem; font-weight: 780; }
.result-copy {
    font-size: .76rem;
    opacity: .63;
    margin-top: .15rem;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-baseweb="select"] > div {
    border-radius: 13px !important;
}
div.stButton > button,
div[data-testid="stDownloadButton"] > button {
    border-radius: 14px !important;
    min-height: 3rem;
    font-weight: 750 !important;
    border: 1px solid var(--border) !important;
}
div.stButton > button[kind="primary"] {
    box-shadow: 0 12px 28px rgba(124,58,237,.18);
}
[data-testid="stFileUploader"] { border-radius: 16px !important; }
[data-testid="stMetric"] {
    border: 1px solid var(--border);
    padding: .7rem .8rem;
    border-radius: 16px;
    background: rgba(255,255,255,.018);
}
hr { border-color: var(--border) !important; }
@media (max-width: 900px) {
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .hero { padding: 1.6rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <div class="eyebrow">✦ PERSONALIZED AI LEARNING</div>
  <h1>Your topic. Your time. Your complete study pack.</h1>
  <p>
    Turn class notes or any subject into structured revision material with a
    five-stage AI workflow that plans, teaches, tests, reviews, and refines before
    showing you the final result.
  </p>
  <div class="hero-pills">
    <span class="hero-pill">🧭 Smart learning plan</span>
    <span class="hero-pill">📚 Exam-focused notes</span>
    <span class="hero-pill">🃏 Flashcards</span>
    <span class="hero-pill">📝 Custom MCQs</span>
    <span class="hero-pill">🔎 Quality review</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


def get_api_key():
    secret_key = ""
    try:
        secret_key = st.secrets.get("SENSENOVA_API_KEY", "")
    except Exception:
        pass
    return secret_key or os.getenv("SENSENOVA_API_KEY", "")


stored_api_key = get_api_key()

with st.sidebar:
    st.markdown(
        """
<div class="sidebar-brand">
  <div class="sidebar-title">🎓 Study Settings</div>
  <div class="sidebar-copy">Choose how deep, how long, and how much practice you want.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if stored_api_key:
        api_key = stored_api_key
    else:
        api_key = st.text_input(
            "SenseNova API Key",
            type="password",
            help="For deployment, add SENSENOVA_API_KEY in Streamlit Secrets.",
        )

    level = st.selectbox(
        "Knowledge Level",
        ["Beginner", "Intermediate", "Advanced"],
        key="level",
        help="Controls explanation depth and assessment difficulty.",
    )

    study_time = st.selectbox(
        "Available Study Time",
        ["30 minutes", "1 hour", "2 hours", "3 hours", "1 day", "3 days", "1 week"],
        key="study_time",
        help="The study plan will be designed around this time.",
    )

    quiz_count = st.select_slider(
        "Number of Quiz Questions",
        options=[5, 10, 15, 20],
        key="quiz_count",
        help="The Assessment Agent will generate this many MCQs.",
    )

    study_mode = st.radio(
        "Study Mode",
        ["Exam Preparation", "Quick Revision", "Deep Understanding"],
        key="study_mode",
        help="Adds an extra focus to the AI's learning goal.",
    )

    st.markdown(
        f"""
<div class="model-box">
  <div class="model-label">AI model</div>
  <div class="model-name">{MODEL_NAME}</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="section-head">
  <div>
    <div class="section-title">⚡ Quick start</div>
    <div class="section-copy">Use a preset or build your own study pack from scratch.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

p1, p2, p3 = st.columns(3)

with p1:
    if st.button("📝 Exam Prep · 2h · 10 MCQs", use_container_width=True):
        apply_preset("", "Prepare efficiently for an upcoming exam with high-yield concepts and practice.", "Intermediate", "2 hours", 10, "Exam Preparation")
        st.rerun()

with p2:
    if st.button("⚡ Quick Revision · 1h · 5 MCQs", use_container_width=True):
        apply_preset("", "Revise the most important concepts quickly and identify gaps.", "Beginner", "1 hour", 5, "Quick Revision")
        st.rerun()

with p3:
    if st.button("🧠 Deep Study · 3h · 15 MCQs", use_container_width=True):
        apply_preset("", "Build deep conceptual understanding with examples and challenging practice.", "Advanced", "3 hours", 15, "Deep Understanding")
        st.rerun()

st.markdown(
    f"""
<div class="stats-grid">
  <div class="stat-card"><div class="stat-label">Level</div><div class="stat-value">🎯 {level}</div></div>
  <div class="stat-card"><div class="stat-label">Study Time</div><div class="stat-value">⏱️ {study_time}</div></div>
  <div class="stat-card"><div class="stat-label">Quiz Size</div><div class="stat-value">📝 {quiz_count} MCQs</div></div>
  <div class="stat-card"><div class="stat-label">Mode</div><div class="stat-value">✨ {study_mode}</div></div>
</div>
""",
    unsafe_allow_html=True,
)

left, right = st.columns([1.08, 0.92], gap="large")

with left:
    st.markdown(
        """
<div class="section-head">
  <div>
    <div class="section-title">📘 Build your study pack</div>
    <div class="section-copy">Start with a topic, then optionally add your own notes or files.</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    topic = st.text_input("Topic / Subject", key="topic", placeholder="e.g. Operating Systems - Memory Management")
    learning_goal = st.text_input("Learning Goal", key="learning_goal", placeholder="e.g. Prepare for my university midterm")
    notes = st.text_area("Notes / Syllabus", key="notes", placeholder="Paste lecture notes, chapter outline, important concepts, or syllabus points...", height=210)
    uploaded_file = st.file_uploader("Upload study material", type=["pdf", "txt", "md"], help="Optional. Supported formats: PDF, TXT, MD.")

    source_kind = "Uploaded file" if uploaded_file else ("Pasted notes" if notes.strip() else "General knowledge")
    c1, c2 = st.columns(2)
    c1.metric("Source", source_kind)
    c2.metric("Quiz questions", quiz_count)

with right:
    st.markdown(
        """
<div class="section-head">
  <div>
    <div class="section-title">🧠 AI workflow</div>
    <div class="section-copy">Five specialized stages collaborate on the final output.</div>
  </div>
</div>

<div class="glass-card card-pad">
  <div class="workflow-grid">
    <div class="flow-item"><div class="flow-icon">🧭</div><div><div class="flow-title">1. Planning</div><div class="flow-copy">Maps objectives, priorities, misconceptions and study order.</div></div></div>
    <div class="flow-item"><div class="flow-icon">📚</div><div><div class="flow-title">2. Content Generation</div><div class="flow-copy">Creates explanations, exam notes, examples and memory aids.</div></div></div>
    <div class="flow-item"><div class="flow-icon">📝</div><div><div class="flow-title">3. Assessment</div><div class="flow-copy">Builds flashcards, short questions and your selected number of MCQs.</div></div></div>
    <div class="flow-item"><div class="flow-icon">🔎</div><div><div class="flow-title">4. Review</div><div class="flow-copy">Checks accuracy, coverage, level and assessment alignment.</div></div></div>
    <div class="flow-item"><div class="flow-icon">✨</div><div><div class="flow-title">5. Refinement</div><div class="flow-copy">Uses review feedback to produce the polished final study pack.</div></div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="section-head" style="margin-top:1.35rem">
  <div>
    <div class="section-title">✨ What your pack includes</div>
    <div class="section-copy">A complete revision bundle, not just a block of AI-generated text.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

f1, f2, f3, f4 = st.columns(4)
feature_data = [
    ("📚", "Smart Notes", "Core concepts, exam-focused explanations, examples and terminology."),
    ("🃏", "Active Recall", "Flashcards and self-check prompts designed for revision."),
    ("📝", "Custom Quiz", f"Exactly {quiz_count} MCQs plus short and conceptual questions."),
    ("📅", "Study Plan", f"A personalized plan designed around your available {study_time}."),
]

for col, (icon, title, copy) in zip([f1, f2, f3, f4], feature_data):
    with col:
        st.markdown(
            f"""
<div class="feature-card">
  <div class="feature-icon">{icon}</div>
  <div class="feature-title">{title}</div>
  <div class="feature-copy">{copy}</div>
</div>
""",
            unsafe_allow_html=True,
        )

st.write("")
generate_col, reset_col = st.columns([4, 1])

with generate_col:
    generate_clicked = st.button("✨ Generate Personalized Study Pack", type="primary", use_container_width=True)

with reset_col:
    if st.button("↻ Reset", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.session_state.pop("study_context", None)
        st.rerun()

if generate_clicked:
    if not api_key:
        st.error("SenseNova API key is missing. Add it in Streamlit Secrets or enter it in the sidebar.")
        st.stop()

    if not topic.strip():
        st.error("Please enter a topic or subject.")
        st.stop()

    try:
        file_text = read_uploaded_file(uploaded_file)
        source_notes = combine_source_text(notes, file_text)
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    mode_instruction = {
        "Exam Preparation": "Prioritize high-yield exam concepts, likely misconceptions, and exam-style practice.",
        "Quick Revision": "Prioritize concise revision, memory aids, key facts, and fast active recall.",
        "Deep Understanding": "Prioritize deeper conceptual explanations, intuition, examples, and connections.",
    }[study_mode]

    combined_goal = f"{learning_goal.strip()}. {mode_instruction}" if learning_goal.strip() else mode_instruction

    progress = st.progress(0, text="Starting your AI workflow...")
    message = st.empty()

    progress_map = {
        "planning": (12, "🧭 Building your learning strategy..."),
        "content_generation": (34, "📚 Creating personalized study notes..."),
        "assessment": (56, f"📝 Generating {quiz_count} quiz questions and assessments..."),
        "review": (76, "🔎 Reviewing accuracy, coverage and quality..."),
        "refinement": (92, "✨ Applying review feedback and polishing the pack..."),
        "done": (100, "✅ Your study pack is ready."),
    }

    def update_progress(stage, ctx):
        percentage, text = progress_map.get(stage, (0, stage))
        progress.progress(percentage, text=text)
        message.caption(text)

    try:
        context = execute_workflow(
            api_key=api_key,
            topic=topic,
            level=level,
            study_time=study_time,
            quiz_count=quiz_count,
            learning_goal=combined_goal,
            source_notes=source_notes,
            progress_callback=update_progress,
        )

        st.session_state["study_context"] = context
        progress.progress(100, text="✅ Study pack complete")
        message.success("Your personalized study pack has been generated successfully.")
    except Exception as exc:
        message.error(f"Workflow failed: {exc}")

context = st.session_state.get("study_context")

if context:
    st.divider()

    st.markdown(
        f"""
<div class="result-banner">
  <div class="result-title">✅ Study pack ready for {context.topic}</div>
  <div class="result-copy">The workflow completed with planning, assessment, quality review and final refinement.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### 📊 Workflow completion")
    columns = st.columns(5)
    stage_names = [
        ("planning", "Planning"),
        ("content_generation", "Content"),
        ("assessment", "Assessment"),
        ("review", "Review"),
        ("refinement", "Refinement"),
    ]

    status_icon = {"success": "🟢", "fallback": "🟠", "failed": "🔴", "running": "🟡", "pending": "⚪"}

    for column, (key, label) in zip(columns, stage_names):
        record = context.stages[key]
        with column:
            st.markdown(
                f"""
<div class="stage-card">
  <div class="stage-icon">{status_icon.get(record.status, "⚪")}</div>
  <div class="stage-label">{label}</div>
  <div class="stage-status">{record.status.title()}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    if context.errors:
        with st.expander("⚠️ Workflow warnings"):
            for error in context.errors:
                st.warning(error)

    st.write("")
    final_tab, plan_tab, review_tab, details_tab = st.tabs(
        ["🎓 Final Study Pack", "🧭 Learning Plan", "🔎 AI Review", "🧩 Workflow Details"]
    )

    with final_tab:
        st.markdown(context.final_pack)
        st.download_button(
            "⬇️ Download Study Pack",
            data=context.final_pack,
            file_name=f"{context.topic.replace(' ', '_')}_study_pack.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with plan_tab:
        st.markdown(context.plan)

    with review_tab:
        st.markdown(context.review)

    with details_tab:
        st.json(
            {
                "topic": context.topic,
                "level": context.level,
                "study_time": context.study_time,
                "quiz_count": context.quiz_count,
                "learning_goal": context.learning_goal,
                "stages": context.stage_summary(),
                "errors": context.errors,
            }
        )

st.markdown(
    """
<div style="text-align:center; opacity:.45; font-size:.72rem; margin-top:2.5rem;">
  Built with Streamlit · SenseNova · Multi-stage AI workflow
</div>
""",
    unsafe_allow_html=True,
)
