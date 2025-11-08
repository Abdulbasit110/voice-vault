from agents import Agent, function_tool
from typing import Dict, Any, Optional
import re

def _security_validate_impl(intent_action: Optional[str] = None, intent_asset: Optional[str] = None, intent_amount: Optional[float] = None, intent_destination: Optional[str] = None) -> Dict[str, Any]:
    """Basic security checks: destination format, positive amounts, known assets."""
    reasons = []
    valid = True

    action = intent_action
    asset = intent_asset
    amount = intent_amount
    dest = intent_destination

    # Normalize "send" to "transfer"
    if action == "send":
        action = "transfer"

    # Action check disabled for now - allow any action
    # if action not in {"buy", "sell", "transfer"}:
    #     valid = False
    #     reasons.append("Unsupported action")

    if asset and asset not in {"USDC", "ETH", "BTC"}:
        valid = False
        reasons.append("Unsupported asset")

    if amount is not None and amount <= 0:
        valid = False
        reasons.append("Amount must be positive")

    if dest and not re.match(r"^0x[a-fA-F0-9]{40}$", dest):
        valid = False
        reasons.append("Invalid destination address")

    return {"valid": valid, "reasons": reasons}

@function_tool
def security_validate(intent_action: Optional[str] = None, intent_asset: Optional[str] = None, intent_amount: Optional[float] = None, intent_destination: Optional[str] = None) -> Dict[str, Any]:
    """Basic security checks: destination format, positive amounts, known assets."""
    return _security_validate_impl(intent_action, intent_asset, intent_amount, intent_destination)


def build_security_validator_agent() -> Agent:
    instructions = (
        "You are the Security Validator. Use the provided tool to validate destination addresses, "
        "amount ranges, and supported assets."
    )
    agent = Agent(
        name="SecurityValidatorAgent",
        instructions=instructions,
        tools=[security_validate],
        model="gpt-4o-mini",
    )
    return agent
