# Career Navigator — Agents for Good
## Kaggle Writeup
**Track:** Agents for Good
**Author:** Suhruth
**Built for:** Google & Kaggle's 5-Day AI Agents Intensive Vibe Coding Course, Capstone Project

---

## The problem

Career coaching, resume review, and interview prep are often gated behind
expensive services or an existing professional network — exactly the
things first-generation job seekers and career changers are least likely
to have. A friend who already works in tech, a paid resume reviewer, a
mentor who'll do a mock interview: all of it compounds an advantage for
people who already have some. The people who'd benefit most from
structured, honest career guidance are frequently the ones with the least
access to it.

## The solution

**Career Navigator** is a multi-agent AI assistant that packages three
things a first-gen job seeker usually has to find (and often pay for)
elsewhere: ATS-optimized resume review, practical career strategy
(networking, upskilling, negotiation), and mock interview practice — with
memory that carries context between all three, so the experience feels
like one continuous relationship with a career coach rather than three
disconnected tools.

It's deliberately built to run with **zero cost and zero cloud
infrastructure barriers**: no GCP billing account, no paid third-party API
key. The only requirement is a free Gemini API key. This was a
conscious design choice, not a limitation — the population this is meant
to serve often doesn't have a credit card to put on a cloud billing
account either, so "free and installable in ten minutes" mattered as much
as any individual feature.

## Architecture

```
career_navigator/                 (root_agent — orchestrator)
├── agent.py                      Routes requests, holds user profile
│                                  in session memory
├── guardrails.py                 Security: redacts PII before it reaches
│                                  the LLM, hard-blocks PII from any tool call
├── resources/                    Curated local knowledge base (markdown)
└── sub_agents/
    ├── resume_agent/             ATS scoring rubric (skill) → scores a
    │                              resume, saves results to memory
    ├── resource_navigator_agent/ MCP server (filesystem) → reads
    │                              resources/ for career strategy guidance
    └── interview_prep_agent/     Question bank (skill) → mock interview
                                   practice, references resume gaps
```

The orchestrator routes each message to the right specialist and holds
top-level session state (the user's target role, location). Each
specialist has its own domain-specific skill or tool, and all three write
back to shared session memory, so — for example — the Interview Prep
Agent can reference a weakness the Resume Agent already flagged, without
the user repeating themselves.

## Concepts demonstrated

| # | Concept | Implementation |
|---|---|---|
| 1 | **Multi-agent system (ADK)** | Root orchestrator + 3 specialist sub-agents, using `transfer_to_agent` handoffs |
| 2 | **MCP server** | Resource Navigator Agent connects to the official `@modelcontextprotocol/server-filesystem` MCP server via `McpToolset`, reading a local curated knowledge base |
| 3 | **Agent skills** | An ATS scoring rubric (5 weighted categories, 100 points) for the Resume Agent, and a categorized interview question bank + feedback rubric for the Interview Prep Agent — structured, reusable domain knowledge rather than one-off prompt text |
| 4 | **Memory / session state** | User profile, resume scores, and interview practice history persist across the conversation and are shared across agents |
| 5 | **Security guardrails** | A `before_model_callback` redacts PII (SSN, credit card, bank account patterns) before it ever reaches the LLM; a `before_tool_callback` hard-blocks PII from reaching any tool call. Verified live: sending a fake SSN increments a `security:redaction_count` in session state, confirming the custom guardrail — not just the model's own training — is what intercepts it. |

## Try it yourself

Full setup instructions, prerequisites, and a walkthrough of all 5
concepts are in the repo README

It runs entirely locally via `adk web` — no cloud deployment required to
try it.

## What I learned building this

The most useful debugging turned out to be Google Cloud / environment
plumbing, not the agent logic itself:
- A version mismatch between an old `aiohttp` install and what the Gemini
  SDK expected produced a confusing `AttributeError` that had nothing to
  do with my code.
- A Gemini API key created inside an existing GCP project (one I'd used
  for an earlier codelab) inherited API restrictions that blocked it —
  creating a fresh key in a fresh project sidestepped this entirely.
- The MCP filesystem server's tools silently failed to register at all
  when Node.js wasn't installed on the machine — no clear error pointed
  at "install Node," just a confusing "tool not found" from the agent
  itself.

None of these were agent-design problems; they were exactly the kind of
environment friction a first-time builder (or, fittingly, a first-gen job
seeker trying to set up their own tools without a mentor to ask) runs
into. That made debugging this project feel like a small, direct
validation of why the project exists.

## Known limitations / honest scope notes

- The local knowledge base is small and hand-curated for this demo — a
  natural next step is growing it, or pointing the same MCP pattern at a
  larger live data source.
- Resume review takes pasted text (or a file dropped into the ADK web
  UI's chat, which Gemini reads natively) rather than a dedicated upload
  flow.
- The PII guardrail patterns (SSN, credit card, bank account) are
  intentionally narrow — a production version would need broader,
  more robust PII detection.
- This build intentionally skips live cloud deployment (Cloud Run /
  Agent Runtime) in favor of being runnable by anyone without a billing
  account — a natural extension, not a missing requirement.

## Closing

Career Navigator started from a simple premise: the guidance that helps
people break into a first career shouldn't require already knowing
someone who works in one. Multi-agent orchestration, a local MCP server,
structured agent skills, cross-agent memory, and real security guardrails
came together here in service of that — free to run, honest about its
limits, and built to actually be used.
