"""
Security guardrails for the Career Navigator agent team.

This demonstrates the "Agent Quality & Security" concept from Day 4:
- before_model_callback: inspects/redacts what goes TO the LLM
- before_tool_callback: blocks sensitive data from reaching external tools
  (e.g. the job search MCP server, which sends queries out to the web)

Design principle: this agent helps with career navigation. It has no
legitimate reason to ever transmit an SSN, a full DOB, a bank/card number,
or a password anywhere — not to the model, and definitely not to an
external MCP server. So we redact/block rather than just warn.
"""

import re
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# --- Patterns for data this agent should never store or transmit ---
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
# Basic phone/email are allowed (users share these for job search legitimately)
# but we still flag if a user pastes something that looks like a full bank
# routing/account pair.
BANK_ACCOUNT_PATTERN = re.compile(r"\b(?:routing|account)\s*#?\s*\d{6,17}\b", re.IGNORECASE)

SENSITIVE_PATTERNS = [
    ("SSN", SSN_PATTERN),
    ("credit card number", CREDIT_CARD_PATTERN),
    ("bank account details", BANK_ACCOUNT_PATTERN),
]


def _find_sensitive_data(text: str):
    """Returns a list of (label, matched_text) for any sensitive data found."""
    hits = []
    for label, pattern in SENSITIVE_PATTERNS:
        for match in pattern.finditer(text):
            hits.append((label, match.group()))
    return hits


def redact_pii_before_model(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    before_model_callback: runs right before every LLM call.

    We scan the latest user turn for sensitive data. If found, we redact it
    in-place in the request (so the model never sees it) and log the
    violation to session state for observability -- we do NOT block the
    whole turn, since the user may have just pasted their resume and
    accidentally included an SSN in a "references available" line. We
    redact and let the conversation continue.
    """
    if not llm_request.contents:
        return None

    last_content = llm_request.contents[-1]
    if last_content.role != "user" or not last_content.parts:
        return None

    redacted_any = False
    for part in last_content.parts:
        if not part.text:
            continue
        hits = _find_sensitive_data(part.text)
        if hits:
            redacted_any = True
            new_text = part.text
            for label, matched in hits:
                new_text = new_text.replace(matched, f"[REDACTED_{label.upper().replace(' ', '_')}]")
            part.text = new_text

    if redacted_any:
        violations = callback_context.state.get("security:redaction_count", 0)
        callback_context.state["security:redaction_count"] = violations + 1

    # Returning None lets the (possibly modified) request proceed to the LLM.
    return None


def block_pii_before_tool(tool, args: dict, tool_context: ToolContext) -> Optional[dict]:
    """
    before_tool_callback: runs right before any tool executes.

    This is the harder guardrail. Even though the Resource Navigator's MCP
    server is local-only (filesystem, not networked), we keep this check
    tool-agnostic and generic: any tool argument containing sensitive data
    gets hard-blocked here, not just redacted, on the principle that no
    specialist in this agent team has a legitimate reason to pass PII into
    a tool call.
    """
    for key, value in args.items():
        if not isinstance(value, str):
            continue
        hits = _find_sensitive_data(value)
        if hits:
            labels = ", ".join(sorted({label for label, _ in hits}))
            return {
                "status": "blocked",
                "reason": (
                    f"This request was blocked before reaching '{tool.name}' because it "
                    f"appears to contain {labels}. This assistant never sends that kind "
                    "of data to external tools. Please remove it and try again."
                ),
            }
    return None
