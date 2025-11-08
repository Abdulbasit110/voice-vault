from agents import Agent, function_tool, ModelSettings, FunctionToolResult, RunContextWrapper, ToolsToFinalOutputResult
from typing import Dict, Any

instructions = (
    "You are the Portfolio Manager. Retrieve current (mock) balances and allocations "
    "via the provided tool. Call the get_mock_portfolio tool to get the portfolio data."
)

def _get_mock_portfolio_data() -> Dict[str, Any]:
    """Return a deterministic mock portfolio for validation (primitive-friendly schema)."""
    return {
        "total_value_usd": 18450.32,
        # balances: [[symbol, amount, usd], ...]
        "balances": [["USDC", 11070.19, 11070.19], ["ETH", 3.0, 4612.58], ["BTC", 0.08, 2767.55]],
        # allocations_pct: [[symbol, percent], ...]
        "allocations_pct": [["USDC", 60.0], ["ETH", 25.0], ["BTC", 15.0]],
        # prices: [[symbol, price], ...]
        "prices": [["USDC", 1.0], ["ETH", 1537.53], ["BTC", 34594.38]],
    }

@function_tool
def get_mock_portfolio() -> Dict[str, Any]:
    """Return a deterministic mock portfolio for validation (primitive-friendly schema)."""
    return _get_mock_portfolio_data()

async def portfolio_tool_behavior(
    context: RunContextWrapper[Any], results: list[FunctionToolResult]
) -> ToolsToFinalOutputResult:
    """Custom tool use behavior that returns the portfolio dict directly."""
    portfolio_dict = results[0].output
    return ToolsToFinalOutputResult(
        is_final_output=True,
        final_output=portfolio_dict
    )

def build_portfolio_manager_agent() -> Agent:
    agent = Agent(
        name="PortfolioManagerAgent",
        instructions=instructions,
        tools=[get_mock_portfolio],
        model="gpt-4o-mini",
        tool_use_behavior=portfolio_tool_behavior,
        model_settings=ModelSettings(tool_choice="required"),
    )
    return agent
