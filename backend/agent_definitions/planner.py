from pydantic import BaseModel
from agents import Agent, function_tool
from typing import Optional
import re

PROMPT = (
    "You are a command parser. Given a natural language command for a financial transaction, "
    "use the parse_natural_command tool to extract the action (buy/sell/transfer), asset (ETH/BTC/USDC), "
    "amount, percentage, and destination address. Return the parsed command structure."
)


class ParsedCommand(BaseModel):
    action: Optional[str] = None        # buy | sell | transfer
    asset: Optional[str] = None         # eth | btc | usdc
    amount: Optional[float] = None      # numeric absolute amount
    percent: Optional[float] = None     # numeric percentage (0-100)
    destination: Optional[str] = None   # address for transfers
    raw: Optional[str] = None           # original text


@function_tool
def parse_natural_command(command_text: str) -> ParsedCommand:
    """Parse a simple NL command into a structured intent."""

    text = (command_text or "").strip().lower()

    # Initialize a model instance
    intent = ParsedCommand(raw=command_text or "")

    # Basic action
    if text.startswith("buy "):
        intent.action = "buy"
    elif text.startswith("sell "):
        intent.action = "sell"
    elif text.startswith("transfer "):
        intent.action = "transfer"

    # Percent e.g., "10%"
    m_pct = re.search(r"(\d+(?:\.\d+)?)%", text)
    if m_pct:
        intent.percent = float(m_pct.group(1))

    # Amount e.g., "0.5" or "100"
    m_amt = re.search(r"\b(\d+(?:\.\d+)?)\b", text)
    if m_amt:
        intent.amount = float(m_amt.group(1))

    # Asset detection
    for sym in ["eth", "btc", "usdc"]:
        if re.search(rf"\b{sym}\b", text):
            intent.asset = sym.upper()
            break

    # Destination address
    m_addr = re.search(r"0x[a-f0-9]{6,}", text)
    if m_addr:
        intent.destination = m_addr.group(0)

    return ParsedCommand(raw=command_text or "", action=intent.action, asset=intent.asset, amount=intent.amount, percent=intent.percent, destination=intent.destination)

def build_planner_agent() -> Agent:
    agent = Agent(
    name="PlannerAgent",
    instructions=PROMPT,
    model="gpt-4o-mini",
    tools=[parse_natural_command],
    output_type=ParsedCommand,
    )
    return agent