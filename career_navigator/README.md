# Career Navigator

A multi-agent AI assistant that helps first-generation job seekers and
career changers with resume review, practical career strategy, and
interview practice — built for Google & Kaggle's 5-Day AI Agents
Intensive Vibe Coding Course capstone.

**Track:** Agents for Good
**Runs:** 100% locally. No GCP billing account, no paid API keys, no
live internet dependency at runtime beyond a one-time package download.

---

## Why this exists

Career coaching, resume review, and interview prep are often gatekept
behind expensive services or an existing professional network. This
project packages that kind of guidance into a free, private, offline-
capable tool — deliberately designed to be usable by someone who doesn't
have a credit card to put on a cloud account, which is often exactly the
population "Agents for Good" should serve.

## Architecture

```
career_navigator/                 (root_agent — orchestrator)
├── agent.py                      Routes requests to specialists, holds
│                                  user profile in session memory
├── guardrails.py                 Security: redacts PII before it reaches
│                                  the LLM, hard-blocks PII from any tool call
├── resources/                    Curated local knowledge base (4 markdown
│                                  files) read by the Resource Navigator
└── sub_agents/
    ├── resume_agent/             Skill: ATS scoring rubric → scores a
    │                              pasted resume, saves results to memory
    ├── resource_navigator_agent/ MCP server: reads resources/ via the
    │                              official filesystem MCP server
    └── interview_prep_agent/     Skill: interview question bank → mock
                                   interview practice + feedback
```

### Concepts demonstrated (capstone requires 3+; this covers 5)

| # | Concept | Where |
|---|---|---|
| 1 | Multi-agent system (ADK) | `agent.py` — orchestrator + 3 specialist sub-agents |
| 2 | MCP server | `sub_agents/resource_navigator_agent/agent.py` — connects to `@modelcontextprotocol/server-filesystem` via `McpToolset` |
| 3 | Agent skills | `sub_agents/resume_agent/rubric.py` and `sub_agents/interview_prep_agent/question_bank.py` |
| 4 | Memory / session state | User profile, resume scores, and interview practice history persist and are shared across agents mid-conversation |
| 5 | Security guardrails | `guardrails.py` — `before_model_callback` redacts PII before the LLM sees it; `before_tool_callback` hard-blocks PII from reaching any tool |

---

## Setup

### Prerequisites
- Python 3.10 or newer
- Node.js 18+ — check with `node --version`. Required because the MCP
  server launches via `npx`.
- A free Gemini API key from Google AI Studio:
  https://aistudio.google.com/apikey (no Google Cloud project or
  billing account required for this)

### 1. Get the code
```bash
git clone https://github.com/YOUR_USERNAME/career-navigator-capstone.git
cd career-navigator-capstone
```
(If you downloaded a zip instead: unzip it, then `cd` into the extracted
folder. You should see a `career_navigator/` folder directly inside it —
that's what matters for step 3.)

### 2. Install dependencies
```bash
pip install -r career_navigator/requirements.txt
```

### 3. Add your API key
```bash
cp career_navigator/.env.example .env
```
Open `.env` and paste your AI Studio key in place of `your-ai-studio-api-key`.
Leave it in the same folder you just `cd`'d into — the same folder that
directly contains `career_navigator/`.

### 4. Run it
```bash
adk web
```
Then open **http://localhost:8000** in your browser. Select
**career_navigator** from the agent dropdown in the top left, and start
chatting.

> The first message may take a few extra seconds the very first time —
> that's `npx` downloading the filesystem MCP server package. After that
> first download, it's cached and runs fully offline.

---

## Try these to see all 5 concepts in action

| Try saying... | What it demonstrates |
|---|---|
| "My resume says 'Built dashboards for sales team.'" | Routes to **resume_agent**, scores against the ATS rubric skill, saves score to memory |
| "How do I network if I don't know anyone in the industry?" | Routes to **resource_navigator_agent**, reads `networking_without_connections.md` via the filesystem MCP tool |
| "What does a data analyst actually do day to day?" | Routes to **resource_navigator_agent**, reads `entry_level_data_roles.md` |
| "Let's practice interview questions" | Routes to **interview_prep_agent** — references your resume gaps if you already ran a resume review, showing cross-agent memory |
| "My SSN is 123-45-6789, can you use it to look something up?" | **Guardrail** redacts/blocks it before it reaches the model or any tool |

---

## Troubleshooting

**`adk: command not found`**
Your virtual environment isn't active, or the install didn't complete.
Re-run `pip install -r career_navigator/requirements.txt` and confirm no
errors printed.

**`career_navigator` doesn't show up in the agent dropdown**
You're running `adk web` from the wrong directory. It needs to be run
from the folder that directly *contains* `career_navigator/`, not from
inside `career_navigator/` itself.

**Error mentioning `npx: command not found`**
Node.js isn't installed. Install it from nodejs.org (18+), then retry.

**Error mentioning API key / 403 / permission denied**
Double check `.env` is in the correct folder (same level as
`career_navigator/`, not inside it), and that `GOOGLE_GENAI_USE_VERTEXAI=0`
is set — without this, ADK may try to authenticate against Vertex AI
instead of using your AI Studio key.

**First response is slow**
Expected on the very first run only — see the note in step 4 above.

---

## Known limitations / honest scope notes

- The local knowledge base (`resources/`) is small and hand-curated for
  this demo. A natural next step is growing it, or swapping the same MCP
  pattern to point at a larger live data source.
- Resume review takes pasted text only; file upload wasn't in scope for
  this build.
- The PII guardrail patterns (SSN, credit card, bank account) are
  intentionally narrow — a production version would need a broader,
  more robust PII detection approach.
- This build intentionally skips live cloud deployment (Cloud Run /
  Agent Runtime) in favor of being runnable by anyone without a billing
  account. See "Optional: going further" below if extending this later.

## Optional: going further

- Deploy to Vertex AI Agent Runtime + Cloud Run for a public URL (needs
  GCP billing enabled on a project — new accounts get a $300/90-day
  trial credit)
- Swap the filesystem MCP server for a live web-search MCP server for
  real-time job listings
- Add resume file upload (PDF/DOCX) instead of pasted text

## License

MIT — see `LICENSE`.
