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
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
.hero {
    padding: 1.5rem 1.7rem;
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 18px;
    margin-bottom: 1.5rem;
}
.hero h1 {
    margin: 0;
}
.hero p {
    opacity: .75;
    margin: .4rem 0 0 0;
}
.stage {
    padding: .7rem;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,.25);
    text-align: center;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
<h1>🎓 AI Study Pack Generator</h1>
<p>Plan → Generate → Assess → Review → Refine with SenseNova AI</p>
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
    st.header("⚙️ Settings")

    if stored_api_key:
        api_key = stored_api_key
        st.success("SenseNova API key loaded securely.")
    else:
        api_key = st.text_input(
            "SenseNova API Key",
            type="password",
            help="For deployment, use Streamlit Secrets instead.",
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

    st.divider()

    st.caption("AI Model")
    st.code(MODEL_NAME, language=None)

    st.caption("Workflow")
    st.markdown(
        """
1. 🧭 Planning
2. 📚 Content
3. 📝 Assessment
4. 🔎 Review
5. ✨ Refinement
"""
    )


# =========================================================
# Inputs
# =========================================================
left, right = st.columns([1.1, 0.9], gap="large")

with left:
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
        placeholder="Paste lecture notes or important syllabus points...",
        height=190,
    )

    uploaded_file = st.file_uploader(
        "Upload Notes",
        type=["pdf", "txt", "md"],
    )

with right:
    st.subheader("🧠 How the workflow works")

    st.markdown(
        """
**1. Planning Agent**  
Breaks the topic into objectives, priorities, and a learning order.

**2. Content Agent**  
Uses the plan to create personalized teaching notes.

**3. Assessment Agent**  
Creates flashcards, MCQs, and questions from the generated content.

**4. Review Agent**  
Checks quality, accuracy, coverage, and assessment alignment.

**5. Refinement Agent**  
Uses all previous outputs and review feedback to produce the final study pack.
"""
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
<small>{record.status.title()}</small>
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
