from typing import Dict, Any

try:
    from openai.types.beta.agents import Agent
    from openai.resources.beta.agents import function_tool
except Exception:  # pragma: no cover
    Agent = object
    def function_tool(*args, **kwargs):
        return None

from backend.tools.agent_tools import mock_execute_transaction


def build_executor_agent() -> Agent:
    """Create Executor agent that performs a dummy transaction execution."""
    exec_tool = function_tool(mock_execute_transaction)

    agent = Agent(
        name="Executor",
        instructions=(
            "You are the Executor. Use the provided tool to perform a mocked transaction execution "
            "and return the transaction_id and status."
        ),
        tools=[exec_tool],
        model="gpt-4o-mini",
    )
    return agent
