from tools.agent_tools import get_mock_portfolio
from agents import Agent

instructions = (
    "You are the Portfolio Manager. Retrieve current (mock) balances and allocations "
    "via the provided tool and summarize key numbers for the other agents."
)

def build_portfolio_manager_agent() -> Agent:
    portfolio_tool = get_mock_portfolio
    agent = Agent(
        name="PortfolioManagerAgent",
        instructions=instructions,
        tools=[portfolio_tool],
        model="gpt-4o-mini",
    )
    return agent
