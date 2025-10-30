from typing import Dict, Any

try:
    from openai.types.beta.agents import Agent
    from openai.resources.beta.agents import function_tool
except Exception:  # pragma: no cover
    Agent = object
    def function_tool(*args, **kwargs):
        return None

from backend.tools.agent_tools import get_mock_portfolio


def build_portfolio_manager_agent() -> Agent:
    """Create Portfolio Manager agent exposing mock portfolio info."""
    portfolio_tool = function_tool(get_mock_portfolio)

    agent = Agent(
        name="PortfolioManager",
        instructions=(
            "You are the Portfolio Manager. Retrieve current (mock) balances and allocations "
            "via the provided tool and summarize key numbers for the other agents."
        ),
        tools=[portfolio_tool],
        model="gpt-4o-mini",
    )
    return agent
