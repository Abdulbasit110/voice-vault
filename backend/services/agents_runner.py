from typing import Any, Dict

import asyncio
from Agents.planner import build_planner_agent
from Agents.portfolio_manager import build_portfolio_manager_agent
from Agents.risk_analyst import build_risk_analyst_agent
from Agents.security_validator import build_security_validator_agent
from Agents.executor import build_executor_agent
from Agents.auditor import build_auditor_agent
from agents import Runner

class AgentRunner:
	"""Full agent-based sequential workflow runner (deterministic)."""
	def __init__(self):
		self.planner_agent = build_planner_agent()
		self.portfolio_agent = build_portfolio_manager_agent()
		self.risk_agent = build_risk_analyst_agent()
		self.security_agent = build_security_validator_agent()
		self.executor_agent = build_executor_agent()
		self.auditor_agent = build_auditor_agent()

	async def run(self, user_text: str):
		print(user_text)

		# 1. Planner
		planner_result = await Runner.run(self.planner_agent, user_text)
		planner_out = getattr(planner_result, "final_output", planner_result)
		print(planner_out)

		# 2. Portfolio Manager
		portfolio_result = await Runner.run(self.portfolio_agent, None)
		portfolio_out = getattr(portfolio_result, "final_output", portfolio_result)
		print(portfolio_out)

		# 3. Risk Analyst (expects intent + portfolio context)
		risk_input = {"intent": planner_out, "portfolio": portfolio_out}
		risk_result = await Runner.run(self.risk_agent, risk_input)
		risk_out = getattr(risk_result, "final_output", risk_result)
		print(risk_out)
		if isinstance(risk_out, dict) and not risk_out.get("approved", True):
			return risk_out
		if hasattr(risk_out, "approved") and not getattr(risk_out, "approved"):
			return risk_out

		# 4. Security Validator (expects intent)
		security_result = await Runner.run(self.security_agent, planner_out)
		security_out = getattr(security_result, "final_output", security_result)
		print(security_out)
		if isinstance(security_out, dict) and not security_out.get("valid", True):
			return security_out
		if hasattr(security_out, "valid") and not getattr(security_out, "valid"):
			return security_out

		# 5. Executor (uses intent)
		exec_result = await Runner.run(self.executor_agent, planner_out)
		exec_out = getattr(exec_result, "final_output", exec_result)
		print(exec_out)

		# 6. Auditor
		tx_id = None
		if isinstance(exec_out, dict):
			tx_id = exec_out.get("transaction_id")
		else:
			tx_id = getattr(exec_out, "transaction_id", None)
		audit_result = await Runner.run(self.auditor_agent, tx_id)
		audit_out = getattr(audit_result, "final_output", audit_result)
		print(audit_out)
		return audit_out