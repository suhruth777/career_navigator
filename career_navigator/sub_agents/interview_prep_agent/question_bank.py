"""
Agent Skill: Interview Question Bank.

Second skill resource, structured the same way as the resume rubric --
categorized, reusable domain content the agent draws from rather than
inventing questions from scratch every time (which tends to produce
generic, low-signal questions).
"""

QUESTION_BANK = {
    "behavioral": [
        "Tell me about a time you had to learn a new tool or system quickly to get a project done.",
        "Describe a situation where you found an error in your own work after presenting it. What did you do?",
        "Tell me about a time a stakeholder disagreed with your analysis or recommendation.",
        "Describe a project where you had to work with incomplete or messy data.",
        "Tell me about a time you had to explain a technical concept to a non-technical audience.",
    ],
    "technical_data": [
        "Walk me through how you'd approach a dataset with significant missing values.",
        "How would you detect and handle duplicate records in a customer table?",
        "Explain the difference between a left join and an inner join, and when you'd use each.",
        "How would you design a KPI dashboard for a stakeholder who's never used one before?",
        "Describe your approach to validating a query's output before presenting results.",
    ],
    "case_estimation": [
        "Estimate how many cigars a mid-size distributor sells in a year. Walk me through your assumptions.",
        "How would you estimate the market size for a new product category your company is considering?",
        "A stakeholder says revenue is down 8% quarter-over-quarter. How do you start investigating?",
    ],
    "closing": [
        "What questions do you have for me about the role or the team?",
        "Why this company, specifically, versus others you might be talking to?",
    ],
}

FEEDBACK_RUBRIC = [
    "Structure: Did the answer have a clear beginning, middle, and end (e.g. STAR for behavioral)?",
    "Specificity: Concrete details (numbers, tools, timeframes) vs. vague generalities?",
    "Relevance: Did the answer actually address what was asked?",
    "Self-awareness: For questions about mistakes/conflict, did they own their part honestly?",
    "Conciseness: Was the answer appropriately tight, or did it wander?",
]


def format_question_bank_as_prompt_context() -> str:
    lines = ["INTERVIEW QUESTION BANK:"]
    for category, questions in QUESTION_BANK.items():
        lines.append(f"\n{category.replace('_', ' ').title()}:")
        for q in questions:
            lines.append(f"  - {q}")
    lines.append("\nFEEDBACK RUBRIC (use when scoring a user's practice answer):")
    for item in FEEDBACK_RUBRIC:
        lines.append(f"  - {item}")
    return "\n".join(lines)
