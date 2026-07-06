"""
Interview Prep Agent.

Runs mock interview practice using the question bank skill, and gives
structured feedback. It also demonstrates cross-agent memory: it reads
resume:top_fixes from session state (written earlier by Resume Agent) so
it can tailor which gaps to probe on, without the user having to repeat
themselves.
"""

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

from ...guardrails import redact_pii_before_model, block_pii_before_tool
from .question_bank import format_question_bank_as_prompt_context


def log_practice_answer(
    question: str,
    strengths: list[str],
    improvements: list[str],
    tool_context: ToolContext,
) -> dict:
    """
    Logs a practice Q&A round to session memory so progress accumulates
    across the conversation instead of every round starting from zero.

    Args:
        question: The interview question that was asked.
        strengths: What the user's answer did well.
        improvements: What to work on next time.
        tool_context: Injected automatically by ADK.
    """
    log = tool_context.state.get("interview:practice_log", [])
    log.append({"question": question, "strengths": strengths, "improvements": improvements})
    tool_context.state["interview:practice_log"] = log
    return {"status": "logged", "total_rounds": len(log)}


INTERVIEW_AGENT_INSTRUCTION = f"""
You are the Interview Prep Agent. You run mock interview practice for job
seekers, especially those without access to formal interview coaching.

{format_question_bank_as_prompt_context()}

Session state may contain resume:top_fixes from an earlier resume review
(check the state for this key). If present, lean toward behavioral
questions that let the user address those gaps out loud -- e.g. if their
resume was flagged for weak quantified impact, ask questions that push
them to practice quantifying their own accomplishments verbally.

Flow:
1. Ask the user which category they want to practice (or pick one that's
   relevant to their target role if they don't specify).
2. Ask ONE question at a time. Wait for their answer before moving on.
3. After each answer, give brief feedback using the feedback rubric, then
   call log_practice_answer to save it.
4. After 3-5 questions, summarize the session: recurring strengths,
   recurring things to work on, and one concrete thing to practice before
   their next real interview.

Keep the tone like a supportive mentor, not a harsh interviewer -- the
goal is building confidence through repetition, not intimidation.
"""

interview_prep_agent = Agent(
    name="interview_prep_agent",
    model="gemini-2.5-flash",
    description=(
        "Runs mock interview practice sessions with behavioral, technical, "
        "and case-style questions, gives structured feedback, and tracks "
        "practice history in memory. Use this agent when the user wants to "
        "practice for an interview or asks what questions to expect."
    ),
    instruction=INTERVIEW_AGENT_INSTRUCTION,
    tools=[log_practice_answer],
    before_model_callback=redact_pii_before_model,
    before_tool_callback=block_pii_before_tool,
)
