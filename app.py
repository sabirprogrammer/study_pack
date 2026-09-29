import os
import streamlit as st

from utils import read_uploaded_file, combine_source_text
from workflow import execute_workflow, MODEL_NAME


st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="🎓",
    layout="wide",
)


# =========================================================
# Styling
# =========================================================
st.markdown(
    """
<style>
:root {
    --border: rgba(128,128,128,.18);
    --soft-bg: rgba(255,255,255,.03);
}

.block-container {
    max-width: 1180px;
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    border-right: 1px solid var(--border);
}

.hero {
    padding: 1.6rem 1.8rem;
    border: 1px solid var(--border);
    border-radius: 22px;
    margin-bottom: 1.2rem;
    background:
        radial-gradient(circle at top right, rgba(72, 149, 239, 0.16), transparent 28%),
        radial-gradient(circle at left bottom, rgba(67, 170, 139, 0.13), transparent 25%),
        rgba(255,255,255,.015);
}

.hero h1 {
    margin: 0;
    font-size: 2.2rem;
    line-height: 1.15;
}

.hero p {
    opacity: .78;
    margin: .45rem 0 0 0;
    font-size: 1rem;
}

.section-card {
    border: 1px solid var(--border);
    background: var(--soft-bg);
    border-radius: 18px;
    padding: 1rem 1rem .9rem 1rem;
    height: 100%;
}

.section-card h3 {
    margin-top: 0;
    margin-bottom: .4rem;
}

.section-card p, .section-card li {
    opacity: .88;
    font-size: .95rem;
}

.mini-card {
    border: 1px solid var(--border);
    background: var(--soft-bg);
    border-radius: 16px;
    padding: .85rem .95rem;
    margin-bottom: .8rem;
}

.mini-label {
    font-size: .78rem;
    opacity: .72;
    margin-bottom: .25rem;
}

.code-pill {
    display: inline-block;
    padding: .45rem .65rem;
    border-radius: 12px;
    background: rgba(255,255,255,.04);
    border: 1px solid var(--border);
    font-family: monospace;
    font-size: .92rem;
}

.workflow-list {
    display: grid;
    grid-template-columns: 1fr;
    gap: .42rem;
    margin-top: .55rem;
}

.workflow-item {
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: .58rem .7rem;
    background: rgba(255,255,255,.025);
    font-size: .93rem;
}

.info-chip {
    display: inline-block;
    padding: .28rem .62rem;
    border-radius: 999px;
    background: rgba(67, 170, 139, 0.12);
    border: 1px solid rgba(67, 170, 139, 0.25);
    font-size: .8rem;
    margin-top: .2rem;
}

.stage {
    padding: .8rem .55rem;
    border-radius: 16px;
    border: 1px solid var(--border);
    text-align: center;
    background: var(--soft-bg);
}

.stage h3 {
    margin: 0 0 .25rem 0;
}

.stage strong {
    font-size: .95rem;
}

.status-text {
    opacity: .72;
    font-size: .8rem;
}

.tip-box {
    border: 1px dashed var(--border);
    border-radius: 16px;
    padding: .9rem 1rem;
    margin-top: .8rem;
    background: rgba(255,255,255,.02);
}

.tight-gap {
    margin-top: .35rem;
}

div[data-testid="stDownloadButton"] > button,
div.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}
.hero-badge{display:inline-flex;padding:.38rem .7rem;border-radius:999px;border:1px solid rgba(139,92,246,.26);background:rgba(139,92,246,.10);font-size:.78rem;font-weight:700;margin-bottom:.75rem}
.feature-row{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1rem}
.feature-pill{padding:.36rem .65rem;border-radius:999px;border:1px solid var(--border);background:rgba(255,255,255,.025);font-size:.78rem}
.sidebar-brand{padding:.95rem 1rem;border:1px solid var(--border);border-radius:18px;background:rgba(255,255,255,.026);margin-bottom:1rem}
.sidebar-brand-title{font-weight:800}.sidebar-brand-copy{opacity:.62;font-size:.77rem;margin-top:.2rem}
.model-chip{margin-top:.9rem;padding:.7rem .8rem;border-radius:14px;border:1px solid var(--border);background:rgba(255,255,255,.02)}
.model-label{opacity:.55;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem;margin-bottom:.22rem}
.model-value{font-family:monospace;font-size:.78rem;opacity:.86;overflow-wrap:anywhere}
.panel{border:1px solid var(--border);border-radius:22px;padding:1.15rem 1.2rem 1rem;background:linear-gradient(180deg,rgba(255,255,255,.032),rgba(255,255,255,.012));box-shadow:0 12px 32px rgba(0,0,0,.08)}
.panel-title{font-size:1.05rem;font-weight:750}.panel-subtitle{opacity:.62;font-size:.84rem;margin-top:.2rem;margin-bottom:.9rem}
.workflow-grid{display:grid;gap:.7rem;margin-top:.8rem}
.workflow-step{display:grid;grid-template-columns:38px 1fr;align-items:center;gap:.75rem;padding:.75rem .8rem;border-radius:15px;border:1px solid var(--border);background:rgba(255,255,255,.02)}
.step-icon{width:36px;height:36px;display:grid;place-items:center;border-radius:11px;background:rgba(139,92,246,.11);border:1px solid rgba(139,92,246,.18)}
.step-name{font-size:.9rem;font-weight:700}.step-copy{font-size:.77rem;opacity:.62;margin-top:.08rem}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <div class="hero-badge">✦ AI-powered study workspace</div>
  <h1>Turn any topic into a complete study pack.</h1>
  <p>Create focused notes, flashcards, quizzes and a personalized study plan through
  a five-stage SenseNova workflow that plans, generates, checks and improves the result.</p>
  <div class="feature-row">
    <span class="feature-pill">🧭 Smart planning</span>
    <span class="feature-pill">📚 Personalized notes</span>
    <span class="feature-pill">📝 Custom quizzes</span>
    <span class="feature-pill">🔎 AI review</span>
    <span class="feature-pill">✨ Final refinement</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# API key
# =========================================================
def get_api_key():
    """
    Priority:
    1. Streamlit Cloud secret
    2. Local environment variable
    3. Optional UI input
    """
    secret_key = ""

    try:
        secret_key = st.secrets.get("SENSENOVA_API_KEY", "")
    except Exception:
        pass

    env_key = os.getenv("SENSENOVA_API_KEY", "")

    return secret_key or env_key


stored_api_key = get_api_key()


# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.markdown(
        """
<div class="sidebar-brand">
  <div class="sidebar-brand-title">🎓 Study Pack Settings</div>
  <div class="sidebar-brand-copy">Personalize difficulty, time and assessment size.</div>
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
            help="For deployment, add the key in Streamlit Secrets.",
        )

    level = st.selectbox(
        "Knowledge Level",
        ["Beginner", "Intermediate", "Advanced"],
    )

    study_time = st.selectbox(
        "Available Study Time",
        [
            "30 minutes",
            "1 hour",
            "2 hours",
            "3 hours",
            "1 day",
            "3 days",
            "1 week",
        ],
        index=2,
        help="The final study plan will fit this time.",
    )

    quiz_count = st.select_slider(
        "Number of Quiz Questions",
        options=[5, 10, 15, 20],
        value=10,
        help="Choose how many multiple-choice questions you want.",
    )

    st.caption(f"Assessment will include **{quiz_count} MCQs**.")

    st.markdown(
        f"""
<div class="model-chip">
  <div class="model-label">AI model</div>
  <div class="model-value">{MODEL_NAME}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# Inputs
# =========================================================
left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown(
        """
<div class="panel">
  <div class="panel-title">📘 Build your study pack</div>
  <div class="panel-subtitle">Give the AI a topic and optional course material.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    topic = st.text_input(
        "Topic / Subject",
        placeholder="Example: Operating Systems - Memory Management",
    )

    learning_goal = st.text_input(
        "Learning Goal",
        placeholder="Example: Prepare for my midterm examination",
    )

    notes = st.text_area(
        "Paste Notes / Syllabus",
        placeholder="Paste lecture notes, outline, or important syllabus points...",
        height=180,
    )

    uploaded_file = st.file_uploader(
        "Upload Notes",
        type=["pdf", "txt", "md"],
        help="Supported files: PDF, TXT, MD",
    )

with right:
    st.markdown(
        """
<div class="panel">
  <div class="panel-title">🧠 Multi-stage AI workflow</div>
  <div class="panel-subtitle">Each stage passes its output forward, so the final pack is reviewed before delivery.</div>
  <div class="workflow-grid">
    <div class="workflow-step"><div class="step-icon">🧭</div><div><div class="step-name">Planning</div><div class="step-copy">Defines objectives, priorities and learning order.</div></div></div>
    <div class="workflow-step"><div class="step-icon">📚</div><div><div class="step-name">Content</div><div class="step-copy">Creates focused notes, examples and key concepts.</div></div></div>
    <div class="workflow-step"><div class="step-icon">📝</div><div><div class="step-name">Assessment</div><div class="step-copy">Builds flashcards and your selected number of MCQs.</div></div></div>
    <div class="workflow-step"><div class="step-icon">🔎</div><div><div class="step-name">Review</div><div class="step-copy">Checks quality, coverage and question alignment.</div></div></div>
    <div class="workflow-step"><div class="step-icon">✨</div><div><div class="step-name">Refinement</div><div class="step-copy">Applies review feedback and creates the final pack.</div></div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# Run workflow
# =========================================================
if st.button(
    "✨ Generate My Study Pack",
    type="primary",
    use_container_width=True,
):
    if not api_key:
        st.error(
            "SenseNova API key is missing. Add it in Streamlit Secrets "
            "or enter it in the sidebar."
        )
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

    progress = st.progress(0)
    message = st.empty()

    progress_map = {
        "planning": (10, "🧭 Planning learning strategy..."),
        "content_generation": (30, "📚 Generating study content..."),
        "assessment": (52, f"📝 Creating {quiz_count} quiz questions..."),
        "review": (70, "🔎 Reviewing quality..."),
        "refinement": (90, "✨ Refining final study pack..."),
        "done": (100, "✅ Workflow completed."),
    }

    def update_progress(stage, ctx):
        percentage, text = progress_map.get(stage, (0, stage))
        progress.progress(percentage)
        message.info(text)

    try:
        context = execute_workflow(
            api_key=api_key,
            topic=topic,
            level=level,
            study_time=study_time,
            quiz_count=quiz_count,
            learning_goal=learning_goal,
            source_notes=source_notes,
            progress_callback=update_progress,
        )

        st.session_state["study_context"] = context

        progress.progress(100)
        message.success("✅ Study pack generated successfully.")

    except Exception as exc:
        message.error(f"Workflow failed: {exc}")


# =========================================================
# Results
# =========================================================
context = st.session_state.get("study_context")

if context:
    st.divider()
    st.subheader("📊 Workflow Status")

    columns = st.columns(5)

    stage_names = [
        ("planning", "Planning"),
        ("content_generation", "Content"),
        ("assessment", "Assessment"),
        ("review", "Review"),
        ("refinement", "Refinement"),
    ]

    status_icon = {
        "success": "🟢",
        "fallback": "🟠",
        "failed": "🔴",
        "running": "🟡",
        "pending": "⚪",
    }

    for column, (key, label) in zip(columns, stage_names):
        record = context.stages[key]

        with column:
            st.markdown(
                f"""
<div class="stage">
  <h3>{status_icon.get(record.status, "⚪")}</h3>
  <strong>{label}</strong><br>
  <span class="status-text">{record.status.title()}</span>
</div>
""",
                unsafe_allow_html=True,
            )

    if context.errors:
        with st.expander("⚠️ Workflow warnings"):
            for error in context.errors:
                st.warning(error)

    final_tab, plan_tab, review_tab, debug_tab = st.tabs(
        [
            "🎓 Final Study Pack",
            "🧭 Planning Output",
            "🔎 Review",
            "🧩 Workflow Context",
        ]
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

    with debug_tab:
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
