from tools.agent_tools import mock_execute_transaction
from agents import Agent

def build_executor_agent() -> Agent:
    exec_tool = mock_execute_transaction
    instructions = (
        "You are the Executor. Use the provided tool to perform a mocked transaction execution "
        "and return the transaction_id and status."
    )
    agent = Agent(
        name="ExecutorAgent",
        instructions=instructions,
        tools=[exec_tool],
        model="gpt-4o-mini",
    )
    return agent
