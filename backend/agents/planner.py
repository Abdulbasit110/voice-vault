from pydantic import BaseModel
from agents import Agent, function_tool
import re

PROMPT = (
    "You are a financial research planner. Given a request for financial analysis, "
    "produce a set of web searches to gather the context needed. Aim for recent "
    "headlines, earnings calls or 10‑K snippets, analyst commentary, and industry background. "
    "Output between 5 and 15 search terms to query for."
)


class ParsedCommand(BaseModel):
    action: str | None = None        # buy | sell | transfer
    asset: str | None = None         # eth | btc | usdc
    amount: float | None = None      # numeric absolute amount
    percent: float | None = None     # numeric percentage (0-100)
    destination: str | None = None   # address for transfers
    raw: str | None = None           # original text


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
    model="o3-mini",
    tools=[parse_natural_command],
    output_type=ParsedCommand,
    )
    return agent