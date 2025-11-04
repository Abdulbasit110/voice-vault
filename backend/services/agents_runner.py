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
		print("running the agent runner")
		print(user_text)

		# 1. Planner
		try:
			print("running the planner agent")
			planner_result = await Runner.run(self.planner_agent, user_text)
			planner_out = getattr(planner_result, "final_output", planner_result)
			print(planner_out)
		except Exception as e:
			print("error in the planner agent")
			print(e)
			return {"error": str(e)}

		# 2. Portfolio Manager
		try:
			portfolio_result = await Runner.run(self.portfolio_agent, {})
			portfolio_out = getattr(portfolio_result, "final_output", portfolio_result)
			print(portfolio_out)
		except Exception as e:
			print("error in the portfolio agent")
			print(e)
			return {"error": str(e)}

		# 3. Risk Analyst (expects intent + portfolio context)
		try:
			print("running the risk agent")
			# Normalize planner output
			if isinstance(planner_out, dict):
				intent_action = planner_out.get("action")
				intent_asset = planner_out.get("asset")
				intent_amount = planner_out.get("amount")
				intent_percent = planner_out.get("percent")
			else:
				intent_action = getattr(planner_out, "action", None)
				intent_asset = getattr(planner_out, "asset", None)
				intent_amount = getattr(planner_out, "amount", None)
				intent_percent = getattr(planner_out, "percent", None)

			# Portfolio is a primitive dict per tool contract
			portfolio_total_value_usd = 0.0
			balances = []
			prices = []
			if isinstance(portfolio_out, dict):
				portfolio_total_value_usd = portfolio_out.get("total_value_usd", 0.0)
				balances = portfolio_out.get("balances", [])
				prices = portfolio_out.get("prices", [])

			risk_input = {
				"intent_action": intent_action,
				"intent_asset": intent_asset,
				"intent_amount": intent_amount,
				"intent_percent": intent_percent,
				"portfolio_total_value_usd": portfolio_total_value_usd,
				"balances": balances,
				"prices": prices,
			}
			risk_result = await Runner.run(self.risk_agent, risk_input)
			risk_out = getattr(risk_result, "final_output", risk_result)
			print(risk_out)
			if isinstance(risk_out, dict) and not risk_out.get("approved", True):
				return risk_out
			if hasattr(risk_out, "approved") and not getattr(risk_out, "approved"):
				return risk_out
		except Exception as e:
			print("error in the risk agent")
			print(e)
			return {"error": str(e)}

		# 4. Security Validator (expects intent)
		try:
			print("running the security agent")
			security_result = await Runner.run(self.security_agent, planner_out)
			security_out = getattr(security_result, "final_output", security_result)
			print(security_out)
			if isinstance(security_out, dict) and not security_out.get("valid", True):
				return security_out
			if hasattr(security_out, "valid") and not getattr(security_out, "valid"):
				return security_out
		except Exception as e:
			print(e)
			print("error in the security agent")
			return {"error": str(e)}

		# 5. Executor (uses intent)
		try:
			print("running the executor agent")
			exec_result = await Runner.run(self.executor_agent, planner_out)
			exec_out = getattr(exec_result, "final_output", exec_result)
			print(exec_out)
		except Exception as e:
			print(e)
			print("error in the executor agent")
			return {"error": str(e)}

		# 6. Auditor
		try:
			print("running the auditor agent")
			tx_id = None
			if isinstance(exec_out, dict):
				tx_id = exec_out.get("transaction_id")
			else:
				tx_id = getattr(exec_out, "transaction_id", None)
			audit_result = await Runner.run(self.auditor_agent, tx_id)
			audit_out = getattr(audit_result, "final_output", audit_result)
			print(audit_out)
		except Exception as e:
			print(e)
			print("error in the auditor agent")
			return {"error": str(e)}

		return audit_out