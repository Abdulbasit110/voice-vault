import uuid
from agents import Agent, function_tool
from typing import Dict, Any, Optional

def _mock_execute_transaction_impl(intent_action: Optional[str] = None, intent_asset: Optional[str] = None, intent_amount: Optional[float] = None, intent_destination: Optional[str] = None) -> Dict[str, Any]:
    """Return a dummy transaction result."""
    return {
        "transaction_id": f"mock_{uuid.uuid4().hex[:8]}",
        "status": "pending",
        "echo_intent": {
            "action": intent_action,
            "asset": intent_asset,
            "amount": intent_amount,
            "destination": intent_destination,
        },
    }

@function_tool
def mock_execute_transaction(intent_action: Optional[str] = None, intent_asset: Optional[str] = None, intent_amount: Optional[float] = None, intent_destination: Optional[str] = None) -> Dict[str, Any]:
    """Return a dummy transaction result."""
    return _mock_execute_transaction_impl(intent_action, intent_asset, intent_amount, intent_destination)


def build_executor_agent() -> Agent:
    instructions = (
        "You are the Executor. Use the provided tool to perform a mocked transaction execution "
        "and return the transaction_id and status."
    )
    agent = Agent(
        name="ExecutorAgent",
        instructions=instructions,
        tools=[mock_execute_transaction],
        model="gpt-4o-mini",
    )
    return agent
