"""
First-Gen Career Navigator -- Root Orchestrator Agent.

Capstone track: Agents for Good.

This is the entry point ADK looks for (`root_agent`). It doesn't do
specialist work itself -- it routes to Resume Agent, Job Search Agent, and
Interview Prep Agent based on what the user needs, and holds the
top-of-conversation memory (the user's profile) that all specialists can
read from.

Concepts demonstrated (capstone requires 3+; this hits 5):
  1. Multi-agent system (ADK)      -> this file: root_agent + 3 sub_agents
  2. MCP server                    -> sub_agents/resource_navigator_agent/agent.py
  3. Agent skills                  -> resume rubric + interview question bank
  4. Memory / session state        -> profile fields here + resume/interview state
  5. Security guardrails           -> guardrails.py, wired in below
"""

from google.adk.agents import Agent

from .guardrails import redact_pii_before_model, block_pii_before_tool
from .sub_agents import resume_agent, resource_navigator_agent, interview_prep_agent
from google.adk.tools.tool_context import ToolContext


def update_user_profile(
    target_role: str,
    target_location: str,
    tool_context: ToolContext,
) -> dict:
    """
    Saves the user's job search profile to session memory so every
    specialist agent can reference it without asking the user to repeat
    themselves each time they switch topics.

    Args:
        target_role: The role/title the user is targeting (e.g. "Data Analyst").
        target_location: Preferred location(s), e.g. "NYC, Chicago, remote".
        tool_context: Injected automatically by ADK.
    """
    tool_context.state["profile:target_role"] = target_role
    tool_context.state["profile:target_location"] = target_location
    return {"status": "saved"}


ROOT_AGENT_INSTRUCTION = """
You are the orchestrator for "Career Navigator" -- a free AI career
assistant for first-generation job seekers and career changers who may not
have access to a personal network, resume coaching, or interview prep
that more privileged candidates often take for granted.

You have three specialists:
- resume_agent: resume review and ATS scoring
- resource_navigator_agent: practical career guidance (role clarity,
  networking without connections, free upskilling, salary negotiation)
  drawn from a curated local knowledge base
- interview_prep_agent: mock interview practice

Your job:
1. On the user's first message, briefly welcome them and ask what they're
   working on right now (resume, job search, or interview prep) if it
   isn't already obvious.
2. If you learn their target role and location and haven't saved it yet,
   call update_user_profile so specialists can use it.
3. Route to the right specialist based on what the user is asking for.
   You can hand off multiple times in one conversation as their needs
   shift -- that's expected and good.
4. Never ask for or store SSNs, dates of birth, bank/card numbers, or
   passwords. None of these specialists need that information for any
   legitimate reason.

Tone: encouraging, direct, and practical. Many users you'll talk to are
navigating the job market with less institutional support than other
candidates -- treat every question as worth a real, useful answer, not a
brush-off.
"""

root_agent = Agent(
    name="career_navigator",
    model="gemini-2.5-flash",
    description="Orchestrates career support for first-gen job seekers.",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[update_user_profile],
    sub_agents=[resume_agent, resource_navigator_agent, interview_prep_agent],
    before_model_callback=redact_pii_before_model,
    before_tool_callback=block_pii_before_tool,
)
