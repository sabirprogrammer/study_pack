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
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <h1>🎓 AI Study Pack Generator</h1>
  <p>Create a personalized study pack with a multi-stage AI workflow:
  <strong>Plan → Generate → Assess → Review → Refine</strong></p>
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
    st.markdown("## ⚙️ Settings")

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
    )

    st.markdown(
        f"""
<div class="mini-card">
  <div class="mini-label">AI Model</div>
  <div class="code-pill">{MODEL_NAME}</div>
</div>

<div class="mini-card">
  <div class="mini-label">Workflow</div>
  <div class="workflow-list">
    <div class="workflow-item">🧭 Planning</div>
    <div class="workflow-item">📚 Content</div>
    <div class="workflow-item">📝 Assessment</div>
    <div class="workflow-item">🔎 Review</div>
    <div class="workflow-item">✨ Refinement</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# Inputs
# =========================================================
left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📘 Study Input")
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
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown(
        """
<div class="section-card">
  <h3>🧠 How the workflow works</h3>
  <p><strong>1. Planning Agent</strong><br>
  Breaks the topic into objectives, concepts, and learning order.</p>

  <p><strong>2. Content Agent</strong><br>
  Creates personalized teaching notes based on the plan.</p>

  <p><strong>3. Assessment Agent</strong><br>
  Builds flashcards, MCQs, and practice questions from the generated content.</p>

  <p><strong>4. Review Agent</strong><br>
  Checks quality, accuracy, coverage, and assessment alignment.</p>

  <p><strong>5. Refinement Agent</strong><br>
  Produces the final polished study pack using all previous outputs.</p>

  <div class="tip-box">
    <strong>Tip:</strong> Paste lecture notes or upload a PDF to get more personalized results.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# Run workflow
# =========================================================
if st.button(
    "✨ Generate Study Pack",
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
        "assessment": (50, "📝 Creating assessments..."),
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
                "learning_goal": context.learning_goal,
                "stages": context.stage_summary(),
                "errors": context.errors,
            }
        )
