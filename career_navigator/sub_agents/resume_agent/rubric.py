"""
Agent Skill: ATS Resume Rubric.

This is the "skill" for the Resume Agent -- a structured, reusable body of
domain knowledge the agent draws on, separate from its conversational
instructions. This mirrors the Day 3 "Context Engineering: Skills" concept:
skills are packaged expertise an agent can be equipped with, rather than
one-off prompt text.

The rubric below is intentionally concrete (weighted categories, point
values) so the agent's scoring is consistent across runs instead of
freeform vibes each time.
"""

ATS_RUBRIC = {
    "categories": [
        {
            "name": "Keyword & Skills Match",
            "weight": 25,
            "checks": [
                "Resume includes hard skills/tools named in the target job description",
                "Skills are demonstrated in bullet points, not just listed once",
                "Job titles align with or reasonably map to industry-standard titles",
            ],
        },
        {
            "name": "Quantified Impact",
            "weight": 25,
            "checks": [
                "Bullets lead with an action verb, not a duty description",
                "Bullets include a metric or scale where possible (%, $, #, time saved)",
                "Impact is tied to a business or team outcome, not just a task completed",
            ],
        },
        {
            "name": "ATS Formatting Compatibility",
            "weight": 20,
            "checks": [
                "No tables, text boxes, columns, or headers/footers that ATS parsers mangle",
                "Standard section headers (Experience, Education, Skills) so parsers recognize them",
                "Consistent, parseable date formats (Month YYYY - Month YYYY)",
                "Saved/exported in a parser-friendly format (.docx or plain-text PDF)",
            ],
        },
        {
            "name": "Structure & Clarity",
            "weight": 15,
            "checks": [
                "Most recent / most relevant experience given the most space",
                "No unexplained gaps or unclear job transitions",
                "One page for <10 years experience unless field norms differ",
            ],
        },
        {
            "name": "Role Fit Narrative",
            "weight": 15,
            "checks": [
                "A reader can tell what role this resume is targeting within 5 seconds",
                "Summary/header line (if present) states a clear value proposition",
                "Experience isn't just a duty log -- it tells a coherent growth story",
            ],
        },
    ]
}


def format_rubric_as_prompt_context() -> str:
    """Renders the rubric as text the agent can reference during scoring."""
    lines = ["ATS RESUME SCORING RUBRIC (100 points total):"]
    for cat in ATS_RUBRIC["categories"]:
        lines.append(f"\n{cat['name']} ({cat['weight']} pts)")
        for check in cat["checks"]:
            lines.append(f"  - {check}")
    return "\n".join(lines)
