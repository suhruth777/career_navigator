"""
Resume Agent.

Specializes in critiquing and scoring resumes against the ATS rubric skill.
Writes its output to session state so the orchestrator and other agents
(e.g. Interview Prep) can reference "the user's current resume score" later
without re-deriving it -- this is the Day 3 "memory" concept in action.
"""

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

from ...guardrails import redact_pii_before_model, block_pii_before_tool
from .rubric import format_rubric_as_prompt_context


def save_resume_score(
    overall_score: int,
    category_scores: dict,
    top_fixes: list[str],
    tool_context: ToolContext,
) -> dict:
    """
    Saves the resume evaluation to session memory so it persists across
    turns and is visible to other agents (e.g. Interview Prep can reference
    "your resume flagged X as a gap").

    Args:
        overall_score: Total score out of 100.
        category_scores: Dict mapping rubric category name -> points earned.
        top_fixes: Ordered list of the highest-impact fixes to make first.
        tool_context: Injected automatically by ADK; gives access to session state.

    Returns:
        Confirmation dict.
    """
    tool_context.state["resume:overall_score"] = overall_score
    tool_context.state["resume:category_scores"] = category_scores
    tool_context.state["resume:top_fixes"] = top_fixes
    return {"status": "saved", "overall_score": overall_score}


RESUME_AGENT_INSTRUCTION = f"""
You are the Resume Agent, a specialist in ATS-optimized resume review for
job seekers -- especially first-generation professionals and career
changers who may not have had access to resume coaching or insider
feedback before.

Use the following rubric to evaluate any resume text or resume summary
the user shares with you:

{format_rubric_as_prompt_context()}

When a user shares resume content:
1. Score each category against the rubric.
2. Compute an overall score out of 100.
3. Identify the 3 highest-impact fixes -- prioritize changes that move the
   score the most, not just any nitpick you notice.
4. Call save_resume_score to persist your evaluation to memory.
5. Present the score and fixes in plain, encouraging language. Many users
   you'll talk to are applying with resumes that were never professionally
   reviewed -- be direct about gaps, but never condescending.

If the user hasn't shared resume content yet, ask them to paste it in
(text is fine, no file upload needed for this MVP).

You do not have access to the user's SSN, financial information, or other
sensitive personal data, and you should never ask for it -- it has no
bearing on resume quality.
"""

resume_agent = Agent(
    name="resume_agent",
    model="gemini-2.5-flash",
    description=(
        "Reviews and scores resumes against an ATS-optimization rubric, "
        "identifies the highest-impact fixes, and saves the evaluation to "
        "session memory. Use this agent whenever the user shares resume "
        "content, asks for resume feedback, or asks about ATS compatibility."
    ),
    instruction=RESUME_AGENT_INSTRUCTION,
    tools=[save_resume_score],
    before_model_callback=redact_pii_before_model,
    before_tool_callback=block_pii_before_tool,
)
