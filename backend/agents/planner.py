from typing import Dict, Any

try:
    # OpenAI Agents SDK imports (ensure package installed in runtime)
    from openai import OpenAI
    from openai.types.beta.agents import Agent
    from openai.types.beta import _agent as agents_beta
    from openai.resources.beta.agents import function_tool
except Exception:  # pragma: no cover
    # Fallback stubs so file can be imported without SDK present
    Agent = object
    def function_tool(*args, **kwargs):
        return None

from backend.tools.agent_tools import parse_natural_command


def build_planner_agent() -> Agent:
    """Create Planner agent that parses NL command to structured intent."""
    parse_tool = function_tool(parse_natural_command)

    planner = Agent(
        name="Planner",
        instructions=(
            "You are the Planner. Parse the user's natural language command into a structured intent with keys: "
            "action, asset, amount, percent, destination. If uncertain, still return your best effort."
        ),
        tools=[parse_tool],
        model="gpt-4o-mini",
    )
    return planner
