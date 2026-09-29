import time
from dataclasses import dataclass, field, asdict
from typing import Callable

from openai import OpenAI


BASE_URL = "https://token.sensenova.ai/v1"
MODEL_NAME = "sensenova-6.8-flash-lite"
MAX_RETRIES = 2


@dataclass
class StageRecord:
    name: str
    status: str = "pending"
    attempts: int = 0
    message: str = ""


@dataclass
class WorkflowContext:
    topic: str
    level: str
    study_time: str
    quiz_count: int = 10
    learning_goal: str = ""
    source_notes: str = ""

    plan: str = ""
    content: str = ""
    assessment: str = ""
    review: str = ""
    final_pack: str = ""

    errors: list[str] = field(default_factory=list)
    stages: dict[str, StageRecord] = field(default_factory=dict)

    def __post_init__(self):
        for name in [
            "planning",
            "content_generation",
            "assessment",
            "review",
            "refinement",
        ]:
            self.stages.setdefault(name, StageRecord(name=name))

    def stage_summary(self):
        return {
            name: asdict(record)
            for name, record in self.stages.items()
        }


def create_client(api_key: str) -> OpenAI:
    if not api_key:
        raise ValueError("SenseNova API key is missing.")

    return OpenAI(
        base_url=BASE_URL,
        api_key=api_key,
    )


def call_sensenova(
    client: OpenAI,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.4,
) -> str:
    """Single reusable SenseNova API call."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )

    content = response.choices[0].message.content

    if not content or not content.strip():
        raise RuntimeError("SenseNova returned an empty response.")

    return content.strip()


def source_context(ctx: WorkflowContext) -> str:
    if ctx.source_notes.strip():
        return f"""
SOURCE MATERIAL:
{ctx.source_notes}

Treat this source material as the primary reference.
Use general knowledge only to explain obvious gaps.
Do not invent unsupported details.
"""
    return """
No source notes were provided.
Use accurate established knowledge about the topic.
"""


def run_stage(
    ctx: WorkflowContext,
    stage_name: str,
    stage_function: Callable[[], str],
    fallback: str = "",
) -> str:
    """Run a stage with retries, status tracking, and optional fallback."""
    record = ctx.stages[stage_name]
    record.status = "running"

    last_error = None

    for attempt in range(1, MAX_RETRIES + 2):
        record.attempts = attempt

        try:
            result = stage_function()

            if not result.strip():
                raise RuntimeError("Stage returned no content.")

            record.status = "success"
            record.message = f"Completed in {attempt} attempt(s)."
            return result

        except Exception as exc:
            last_error = exc
            record.message = str(exc)

            if attempt <= MAX_RETRIES:
                time.sleep(attempt)

    error_message = f"{stage_name} failed: {last_error}"
    ctx.errors.append(error_message)

    if fallback:
        record.status = "fallback"
        record.message = error_message
        return fallback

    record.status = "failed"
    raise RuntimeError(error_message)


# =========================================================
# Stage 1: Planning
# =========================================================
def planning_stage(client: OpenAI, ctx: WorkflowContext) -> str:
    return call_sensenova(
        client,
        system_prompt=(
            "You are the Planning Agent of an AI study-pack workflow. "
            "Your job is to design the learning strategy, not write the full study pack."
        ),
        user_prompt=f"""
Create a personalized study plan.

Topic: {ctx.topic}
Knowledge level: {ctx.level}
Available study time: {ctx.study_time}
Learning goal: {ctx.learning_goal or "Understand the topic and prepare for assessment"}

{source_context(ctx)}

Return Markdown containing:

## Learning Objectives
## Prerequisites
## Topic Decomposition
## Priority Concepts
## Time Allocation
## Common Misconceptions
## Assessment Strategy

Keep the plan concise and actionable.
""",
        temperature=0.25,
    )


# =========================================================
# Stage 2: Content Generation
# =========================================================
def content_generation_stage(client: OpenAI, ctx: WorkflowContext) -> str:
    return call_sensenova(
        client,
        system_prompt=(
            "You are the Content Generation Agent. "
            "Follow the Planner's strategy and create accurate teaching material."
        ),
        user_prompt=f"""
Topic: {ctx.topic}
Level: {ctx.level}
Study time: {ctx.study_time}

PLANNER OUTPUT:
{ctx.plan}

{source_context(ctx)}

Generate Markdown with:

## Quick Overview
## Learning Objectives
## Core Concepts
## Exam-Focused Notes
## Worked Examples / Intuition
## Important Terms
Use a Markdown table for important terms.
## Memory Aids

Do not create quizzes yet.
Avoid unnecessary repetition.
Adapt the explanation to the learner's level.
""",
        temperature=0.4,
    )


# =========================================================
# Stage 3: Assessment
# =========================================================
def assessment_stage(client: OpenAI, ctx: WorkflowContext) -> str:
    return call_sensenova(
        client,
        system_prompt=(
            "You are the Assessment Agent. "
            "Create assessments that test only concepts taught in the generated material."
        ),
        user_prompt=f"""
Topic: {ctx.topic}
Level: {ctx.level}

PLANNER OUTPUT:
{ctx.plan}

GENERATED CONTENT:
{ctx.content}

Create:

## Flashcards
10 question/answer flashcards.

## Multiple-Choice Quiz
Create exactly {ctx.quiz_count} MCQs with A-D choices.

## Quiz Answer Key
Correct option plus a one-line explanation.

## Short Questions
5 short-answer questions.

## Long / Conceptual Questions
3 deeper questions.

## Self-Check
5 statements beginning with "I can..."
""",
        temperature=0.4,
    )


# =========================================================
# Stage 4: Review
# =========================================================
def review_stage(client: OpenAI, ctx: WorkflowContext) -> str:
    return call_sensenova(
        client,
        system_prompt=(
            "You are the Review Agent. "
            "Act as a strict quality checker for the study-pack draft."
        ),
        user_prompt=f"""
Learner topic: {ctx.topic}
Level: {ctx.level}
Available time: {ctx.study_time}
Goal: {ctx.learning_goal or "General study and assessment preparation"}

PLAN:
{ctx.plan}

CONTENT:
{ctx.content}

ASSESSMENT:
{ctx.assessment}

{source_context(ctx)}

Check:

1. factual consistency
2. source alignment
3. missing important concepts
4. learner-level suitability
5. duplicated material
6. unclear explanations
7. quiz/content mismatch
8. exam relevance
9. whether material fits available study time

Return:

## Review Summary
## Issues Found
## Required Improvements
## Quality Decision

Quality Decision must be either:
PASS
or
NEEDS_REFINEMENT
""",
        temperature=0.15,
    )


# =========================================================
# Stage 5: Refinement
# =========================================================
def refinement_stage(client: OpenAI, ctx: WorkflowContext) -> str:
    return call_sensenova(
        client,
        system_prompt=(
            "You are the Refinement Agent. "
            "Create the final polished study pack using all previous workflow context."
        ),
        user_prompt=f"""
TOPIC: {ctx.topic}
LEVEL: {ctx.level}
AVAILABLE STUDY TIME: {ctx.study_time}
LEARNING GOAL: {ctx.learning_goal or "General study and assessment preparation"}

PLAN:
{ctx.plan}

CONTENT DRAFT:
{ctx.content}

ASSESSMENT:
{ctx.assessment}

REVIEW FEEDBACK:
{ctx.review}

{source_context(ctx)}

Produce one final Markdown study pack.

# AI Study Pack: {ctx.topic}

## 1. Quick Overview
## 2. Learning Objectives
## 3. Core Concepts
## 4. Exam-Focused Notes
## 5. Worked Examples / Intuition
## 6. Important Terms
## 7. Memory Aids
## 8. Flashcards
## 9. Multiple-Choice Quiz
Include exactly {ctx.quiz_count} MCQs with A-D choices.
## 10. Quiz Answer Key
Include one answer entry for every MCQ.
## 11. Short Questions
## 12. Long / Conceptual Questions
## 13. Personalized Study Plan
Make the schedule fit within {ctx.study_time}.
## 14. Final Revision Checklist
## 15. Self-Check

Apply important reviewer corrections.
Remove contradictions and unnecessary duplication.
""",
        temperature=0.3,
    )


# =========================================================
# Workflow Orchestrator
# =========================================================
def execute_workflow(
    api_key: str,
    topic: str,
    level: str,
    study_time: str,
    quiz_count: int,
    learning_goal: str,
    source_notes: str,
    progress_callback=None,
) -> WorkflowContext:

    if not topic or not topic.strip():
        raise ValueError("Please enter a topic.")

    client = create_client(api_key)

    ctx = WorkflowContext(
        topic=topic.strip(),
        level=level,
        study_time=study_time,
        quiz_count=int(quiz_count),
        learning_goal=(learning_goal or "").strip(),
        source_notes=(source_notes or "").strip(),
    )

    def report(stage_name: str):
        if progress_callback:
            progress_callback(stage_name, ctx)

    report("planning")
    ctx.plan = run_stage(
        ctx,
        "planning",
        lambda: planning_stage(client, ctx),
        fallback=f"""
## Emergency Learning Plan
Focus on the fundamental concepts of {ctx.topic}.
Move from definitions to examples, then use active recall and practice questions.
Reserve the final part of {ctx.study_time} for revision.
""",
    )

    report("content_generation")
    ctx.content = run_stage(
        ctx,
        "content_generation",
        lambda: content_generation_stage(client, ctx),
    )

    report("assessment")
    ctx.assessment = run_stage(
        ctx,
        "assessment",
        lambda: assessment_stage(client, ctx),
        fallback="""
## Assessment
Automatic assessment generation failed.
Use each core-concept heading as an active-recall question and explain it without notes.
""",
    )

    report("review")
    ctx.review = run_stage(
        ctx,
        "review",
        lambda: review_stage(client, ctx),
        fallback="""
## Review Summary
Automated review was unavailable.

## Required Improvements
Manually verify factual accuracy, difficulty, coverage, duplication, and assessment alignment.

## Quality Decision
NEEDS_REFINEMENT
""",
    )

    report("refinement")

    try:
        ctx.final_pack = run_stage(
            ctx,
            "refinement",
            lambda: refinement_stage(client, ctx),
        )
    except Exception:
        ctx.final_pack = (
            f"# AI Study Pack: {ctx.topic}\n\n"
            + ctx.content
            + "\n\n"
            + ctx.assessment
            + f"\n\n## Personalized Study Plan\n"
              f"Use the available {ctx.study_time} by studying core concepts first, "
              "then testing yourself and finishing with revision."
        )
        ctx.errors.append(
            "Refinement failed, so the best available draft was returned."
        )

    report("done")
    return ctx
