from typing import Dict, Any

try:
    from openai.types.beta.agents import Agent
    from openai.resources.beta.agents import function_tool
except Exception:  # pragma: no cover
    Agent = object
    def function_tool(*args, **kwargs):
        return None

from backend.tools.agent_tools import security_validate


def build_security_validator_agent() -> Agent:
    """Create Security Validator agent to run basic security checks."""
    sec_tool = function_tool(security_validate)

    agent = Agent(
        name="SecurityValidator",
        instructions=(
            "You are the Security Validator. Use the provided tool to validate destination addresses, "
            "amount ranges, and supported assets."
        ),
        tools=[sec_tool],
        model="gpt-4o-mini",
    )
    return agent
