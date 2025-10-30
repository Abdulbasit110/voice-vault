from typing import Dict, Any
import os

try:
    from openai import OpenAI
    from openai.types.beta.agents import Agent
    from openai.resources.beta import agents as agents_api
    from openai.types.beta import Threads
    from openai.types.beta.threads import TextInput
except Exception:  # pragma: no cover
    OpenAI = None

from backend.agents.planner import build_planner_agent
from backend.agents.risk_analyst import build_risk_analyst_agent
from backend.agents.portfolio_manager import build_portfolio_manager_agent
from backend.agents.security_validator import build_security_validator_agent
from backend.agents.executor import build_executor_agent
from backend.agents.auditor import build_auditor_agent
from backend.tools.agent_tools import (
    parse_natural_command,
    get_mock_portfolio,
    basic_risk_check,
    security_validate,
    mock_execute_transaction,
    mock_audit_transaction,
)


class AgenticFlowRunner:
    """Coordinates the end-to-end flow using OpenAI Agents SDK.
    This implementation doesn't rely on long-lived threads; it orchestrates tools deterministically.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OpenAI else None

        # Build agents (metadata/intent). We will call tools directly to keep it deterministic.
        self.planner = build_planner_agent()
        self.portfolio = build_portfolio_manager_agent()
        self.risk = build_risk_analyst_agent()
        self.security = build_security_validator_agent()
        self.executor = build_executor_agent()
        self.auditor = build_auditor_agent()

    def run(self, text: str) -> Dict[str, Any]:
        # 1) Planner parses
        parsed = parse_natural_command(text)

        # 2) Portfolio fetch
        portfolio = get_mock_portfolio()

        # 3) Risk check
        risk_eval = basic_risk_check(parsed, portfolio)

        # 4) Security validation
        sec_eval = security_validate(parsed)

        approved = risk_eval.get("approved", False) and sec_eval.get("valid", False)

        # 5) Execute (mock)
        tx = mock_execute_transaction(parsed) if approved else {"skipped": True}

        # 6) Audit (mock)
        audit = (
            mock_audit_transaction(tx.get("transaction_id", "mock_none")) if approved else {"skipped": True}
        )

        return {
            "approved": approved,
            "parsed": parsed,
            "portfolio": {
                "total_value_usd": portfolio.get("total_value_usd"),
                "allocations_pct": portfolio.get("allocations_pct"),
            },
            "validations": {
                "risk": risk_eval,
                "security": sec_eval,
            },
            "transaction": tx,
            "audit": audit,
        }
