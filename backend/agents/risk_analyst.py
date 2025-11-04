from agents import Agent, function_tool
from typing import List, Optional, Union

RISK_PROMPT = (
    "You are a risk analyst validating transaction safety against simple limits. "
    "Decide approval and list human-readable reasons when blocked."
)

def _basic_risk_check_impl(
    intent_action: Optional[str] = None,
    intent_asset: Optional[str] = None,
    intent_amount: Optional[float] = None, 
    intent_percent: Optional[float] = None,
    portfolio_total_value_usd: float = 0.0,
    balances: List[List[Union[float, str]]] = [],
    prices: List[List[Union[float, str]]] = [],
) -> dict:
    """Very simple thresholds-based risk gate.
    Rules:
    - Percent orders must be <= 50%
    - Absolute buy/sell amount must not exceed 30% of portfolio value (approx)
    - Transfers must be <= $5,000 equivalent
    Inputs avoid nested object schemas to satisfy strict JSON schema.
    balances: [[symbol, amount, usd], ...]
    prices: [[symbol, price], ...]
    """
    reasons: List[str] = []
    approved = True

    percent = intent_percent
    amount = intent_amount
    asset = intent_asset
    action = (intent_action or "").lower() if intent_action else None

    def find_price(sym: Optional[str]) -> float:
        if not sym:
            return 1.0
        for row in prices:
            if len(row) >= 2 and isinstance(row[0], str) and row[0] == sym:
                # row = [symbol, price]
                try:
                    return float(row[1])
                except Exception:
                    return 1.0
        return 1.0

    if percent is not None and percent > 50:
        approved = False
        reasons.append("Percent exceeds 50% limit")

    if amount is not None:
        usd_equiv = amount * find_price(asset)
        source_cap = 0.30 * float(portfolio_total_value_usd or 0.0)
        if usd_equiv > source_cap:
            approved = False
            reasons.append("Amount exceeds 30% portfolio cap")

    if action == "transfer" and amount is not None:
        usd_equiv = amount * find_price(asset)
        if usd_equiv > 5000:
            approved = False
            reasons.append("Transfer exceeds $5,000 limit")

    return {"approved": approved, "reasons": reasons}

@function_tool
def basic_risk_check(
    intent_action: Optional[str] = None,
    intent_asset: Optional[str] = None,
    intent_amount: Optional[float] = None, 
    intent_percent: Optional[float] = None,
    portfolio_total_value_usd: float = 0.0,
    balances: List[List[Union[float, str]]] = [],
    prices: List[List[Union[float, str]]] = [],
) -> dict:
    """Very simple thresholds-based risk gate."""
    return _basic_risk_check_impl(
        intent_action, intent_asset, intent_amount, intent_percent,
        portfolio_total_value_usd, balances, prices
    )

def build_risk_analyst_agent() -> Agent:
    agent = Agent(
        name="RiskAnalystAgent",
        instructions=RISK_PROMPT,
        tools=[basic_risk_check],
        model="gpt-4o-mini",
    )
    return agent