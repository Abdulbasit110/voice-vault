from typing import Dict, Any

try:
    from openai.types.beta.agents import Agent
    from openai.resources.beta.agents import function_tool
except Exception:  # pragma: no cover
    Agent = object
    def function_tool(*args, **kwargs):
        return None

from backend.tools.agent_tools import mock_audit_transaction


def build_auditor_agent() -> Agent:
    """Create Auditor agent that confirms a mocked transaction."""
    audit_tool = function_tool(mock_audit_transaction)

    agent = Agent(
        name="Auditor",
        instructions=(
            "You are the Auditor. Use the provided tool to verify the transaction by id and report confirmation."
        ),
        tools=[audit_tool],
        model="gpt-4o-mini",
    )
    return agent
