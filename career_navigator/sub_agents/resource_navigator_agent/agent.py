"""
Resource Navigator Agent.

Demonstrates the "MCP server" concept the same way the original design
did, but with zero external dependencies: no API key, no billing, no
internet required at runtime. It connects to the official
@modelcontextprotocol/server-filesystem MCP server, pointed at a local
folder of curated career resources, via McpToolset -- the exact same
integration pattern as a networked MCP server, just pointed at local
files instead of a remote API.

The only one-time internet requirement is the first `npx` call, which
downloads the filesystem MCP server package. After that, it runs
entirely offline.
"""

import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from ...guardrails import redact_pii_before_model, block_pii_before_tool

# ADK has used both `McpToolset` and `MCPToolset` as the class name across
# different releases. Try both so this doesn't break on a slightly
# different ADK version than the one this was built against.
try:
    from google.adk.tools.mcp_tool import McpToolset as _ToolsetClass
except ImportError:
    from google.adk.tools.mcp_tool import MCPToolset as _ToolsetClass

# Absolute path to the curated resource folder shipped with this project.
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources")

resource_mcp = _ToolsetClass(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", RESOURCES_DIR],
        ),
        timeout=30,
    ),
    # Read-only tools -- this agent should never write/delete files.
    tool_filter=["read_file", "list_directory"],
)

RESOURCE_NAVIGATOR_INSTRUCTION = """
You are the Resource Navigator Agent. You help first-generation job
seekers find practical, no-cost guidance on breaking into data roles --
role clarity, networking without an existing network, free ways to build
real skills, and salary negotiation.

You have read access to a local folder of curated resource files via
your tools. Use list_directory to see what's available, and read_file to
pull the actual content before answering -- don't guess at what's in a
file from its name alone.

When the user asks something like "what does a data analyst actually
do" or "how do I network without connections" or "how do I negotiate an
offer," find the relevant file, read it, and answer using that content
in your own words -- synthesize and personalize for what you know about
the user from this conversation, don't just paste the file back at them.

If nothing in the local resources answers their question, say so plainly
and give your own best general guidance rather than forcing a fit to
whatever files happen to exist.
"""

resource_navigator_agent = Agent(
    name="resource_navigator_agent",
    model="gemini-2.5-flash",
    description=(
        "Helps first-generation job seekers with practical, no-cost "
        "guidance on role clarity, networking, free upskilling, and "
        "salary negotiation, drawn from a curated local knowledge base. "
        "Use this agent for questions about career strategy that aren't "
        "resume review or interview practice."
    ),
    instruction=RESOURCE_NAVIGATOR_INSTRUCTION,
    tools=[resource_mcp],
    before_model_callback=redact_pii_before_model,
    before_tool_callback=block_pii_before_tool,
)
