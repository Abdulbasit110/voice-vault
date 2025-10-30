import re
import uuid
from typing import Dict, Any, Optional


def parse_natural_command(command_text: str) -> Dict[str, Any]:
    """Parse a simple NL command into a structured intent.

    Supported examples:
    - "buy 0.5 eth"
    - "sell 10% btc"
    - "transfer 100 usdc to 0xabc..."
    """
    text = (command_text or "").strip().lower()

    # Defaults
    intent: Dict[str, Any] = {
        "action": None,        # buy | sell | transfer
        "asset": None,         # eth | btc | usdc (symbol string)
        "amount": None,        # numeric absolute amount
        "percent": None,       # numeric percentage (0-100)
        "destination": None,   # address for transfers
        "raw": command_text or "",
    }

    # Basic action
    if text.startswith("buy "):
        intent["action"] = "buy"
    elif text.startswith("sell "):
        intent["action"] = "sell"
    elif text.startswith("transfer "):
        intent["action"] = "transfer"

    # Percent e.g., "10%"
    m_pct = re.search(r"(\d+(?:\.\d+)?)%", text)
    if m_pct:
        try:
            intent["percent"] = float(m_pct.group(1))
        except ValueError:
            pass

    # Amount e.g., "0.5" or "100"
    m_amt = re.search(r"\b(\d+(?:\.\d+)?)\b", text)
    if m_amt:
        try:
            intent["amount"] = float(m_amt.group(1))
        except ValueError:
            pass

    # Asset simple detection
    for sym in ["eth", "btc", "usdc"]:
        if re.search(rf"\b{sym}\b", text):
            intent["asset"] = sym.upper()
            break

    # Destination address heuristic
    m_addr = re.search(r"0x[a-f0-9]{6,}", text)
    if m_addr:
        intent["destination"] = m_addr.group(0)

    return intent


def get_mock_portfolio() -> Dict[str, Any]:
    """Return a deterministic mock portfolio for validation."""
    return {
        "total_value_usd": 18450.32,
        "balances": {
            "USDC": {"amount": 11070.19, "usd": 11070.19},
            "ETH": {"amount": 3.0, "usd": 4612.58},
            "BTC": {"amount": 0.08, "usd": 2767.55},
        },
        "allocations_pct": {"USDC": 60.0, "ETH": 25.0, "BTC": 15.0},
        # Very rough prices for conversion if needed
        "prices": {"USDC": 1.0, "ETH": 1537.53, "BTC": 34594.38},
    }


def basic_risk_check(intent: Dict[str, Any], portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """Very simple thresholds-based risk gate.
    Rules:
    - Percent orders must be <= 50%
    - Absolute buy/sell amount must not exceed 30% of the source balance (if derivable)
    - Transfers must be <= $5,000 equivalent
    """
    reasons = []
    approved = True

    percent = intent.get("percent")
    amount = intent.get("amount")
    asset = intent.get("asset")
    action = intent.get("action")

    prices = portfolio["prices"]
    balances = portfolio["balances"]

    if percent is not None and percent > 50:
        approved = False
        reasons.append("Percent exceeds 50% limit")

    if amount is not None and asset in balances:
        usd_equiv = amount * (prices.get(asset, 1.0))
        source_cap = 0.30 * portfolio["total_value_usd"]
        if usd_equiv > source_cap:
            approved = False
            reasons.append("Amount exceeds 30% portfolio cap")

    if action == "transfer" and amount is not None:
        usd_equiv = amount * (prices.get(asset, 1.0)) if asset else amount
        if usd_equiv > 5000:
            approved = False
            reasons.append("Transfer exceeds $5,000 limit")

    return {"approved": approved, "reasons": reasons}


def security_validate(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Basic security checks: destination format, positive amounts, known assets."""
    reasons = []
    valid = True

    action = intent.get("action")
    asset = intent.get("asset")
    amount = intent.get("amount")
    dest = intent.get("destination")

    if action not in {"buy", "sell", "transfer"}:
        valid = False
        reasons.append("Unsupported action")

    if asset and asset not in {"USDC", "ETH", "BTC"}:
        valid = False
        reasons.append("Unsupported asset")

    if amount is not None and amount <= 0:
        valid = False
        reasons.append("Amount must be positive")

    if action == "transfer" and (not dest or not re.match(r"^0x[a-f0-9]{6,}$", dest)):
        valid = False
        reasons.append("Invalid destination address")

    return {"valid": valid, "reasons": reasons}


def mock_execute_transaction(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dummy transaction result."""
    return {
        "transaction_id": f"mock_{uuid.uuid4().hex[:8]}",
        "status": "pending",
        "echo_intent": intent,
    }


def mock_audit_transaction(transaction_id: str) -> Dict[str, Any]:
    """Return a dummy audit confirmation."""
    return {
        "transaction_id": transaction_id,
        "confirmed": True,
        "confirmation_hash": f"mock_hash_{uuid.uuid4().hex[:10]}",
    }
