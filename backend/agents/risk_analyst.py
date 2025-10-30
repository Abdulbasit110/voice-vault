from typing import Dict, Any

try:
    from openai.types.beta.agents import Agent
    from openai.resources.beta.agents import function_tool
except Exception:  # pragma: no cover
    Agent = object
    def function_tool(*args, **kwargs):
        return None

from backend.tools.agent_tools import basic_risk_check


def build_risk_analyst_agent() -> Agent:
    """Create Risk Analyst agent that performs simple threshold checks."""
    risk_tool = function_tool(basic_risk_check)

    agent = Agent(
        name="RiskAnalyst",
        instructions=(
            "You are the Risk Analyst. Call the provided tool to evaluate whether the transaction "
            "violates risk thresholds. Summarize reasons if not approved."
        ),
        tools=[risk_tool],
        model="gpt-4o-mini",
    )
    return agent
