from typing import Any, Dict, Optional

import asyncio
from Agents.planner import build_planner_agent
from Agents.portfolio_manager import build_portfolio_manager_agent
from Agents.risk_analyst import build_risk_analyst_agent
from Agents.security_validator import build_security_validator_agent
from Agents.executor import build_executor_agent
from Agents.auditor import build_auditor_agent
from agents import Runner

async def run_with_retry(agent, input_data, max_retries=3, initial_delay=1):
	"""Run an agent with retry logic for transient API errors."""
	for attempt in range(max_retries):
		try:
			result = await Runner.run(agent, input_data)
			return result
		except Exception as e:
			error_str = str(e)
			# Check if it's a retryable error (server_error, rate_limit, etc.)
			is_retryable = (
				"server_error" in error_str.lower() or
				"rate_limit" in error_str.lower() or
				"Error code: 500" in error_str or
				"Error code: 429" in error_str
			)
			
			if is_retryable and attempt < max_retries - 1:
				delay = initial_delay * (2 ** attempt)  # Exponential backoff
				print(f"Retryable error on attempt {attempt + 1}/{max_retries}, retrying in {delay}s...")
				await asyncio.sleep(delay)
				continue
			else:
				# Not retryable or max retries reached
				raise

class AgentRunner:
	"""Full agent-based sequential workflow runner (deterministic)."""
	def __init__(self):
		self.planner_agent = build_planner_agent()
		self.portfolio_agent = build_portfolio_manager_agent()
		self.risk_agent = build_risk_analyst_agent()
		self.security_agent = build_security_validator_agent()
		self.executor_agent = build_executor_agent()
		self.auditor_agent = build_auditor_agent()

	async def run(self, user_text: str, user_id: Optional[str] = None):
		print("running the agent runner")
		print(user_text)
		print(f"user_id: {user_id}")

		# 1. Planner
		try:
			print("running the planner agent")
			planner_result = await run_with_retry(self.planner_agent, user_text)
			planner_out = getattr(planner_result, "final_output", planner_result)
			print(planner_out)
		except Exception as e:
			print("error in the planner agent")
			print(e)
			return {
				"error": str(e),
				"message": f"Error parsing your request: {str(e)}",
				"status": "failed"
			}

		# 2. Portfolio Manager - bypass agent framework to avoid dict.extend() error
		try:
			from Agents.portfolio_manager import _get_mock_portfolio_data
			portfolio_out = _get_mock_portfolio_data()
			print("portfolio_out", portfolio_out)
		except Exception as e:
			print("error in the portfolio agent")
			print(e)
			return {
				"error": str(e),
				"message": f"Error checking portfolio: {str(e)}",
				"status": "failed"
			}

		# 3. Risk Analyst (expects intent + portfolio context) - bypass agent framework
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

			# Portfolio can be a dict or Pydantic model
			portfolio_total_value_usd = 0.0
			balances = []
			prices = []
			if isinstance(portfolio_out, dict):
				portfolio_total_value_usd = portfolio_out.get("total_value_usd", 0.0)
				balances = portfolio_out.get("balances", [])
				prices = portfolio_out.get("prices", [])
			else:
				# Handle Pydantic model
				portfolio_total_value_usd = getattr(portfolio_out, "total_value_usd", 0.0)
				balances = getattr(portfolio_out, "balances", [])
				prices = getattr(portfolio_out, "prices", [])

			from Agents.risk_analyst import _basic_risk_check_impl
			risk_out = _basic_risk_check_impl(
				intent_action=intent_action,
				intent_asset=intent_asset,
				intent_amount=intent_amount,
				intent_percent=intent_percent,
				portfolio_total_value_usd=portfolio_total_value_usd,
				balances=balances,
				prices=prices,
			)
			print("risk_out", risk_out)
			if isinstance(risk_out, dict) and not risk_out.get("approved", True):
				# Add message to risk rejection
				reasons = risk_out.get("reasons", [])
				message = "Transaction rejected by risk analysis. " + "; ".join(reasons) if reasons else "Transaction rejected by risk analysis."
				risk_out["message"] = message
				risk_out["status"] = "rejected"
				return risk_out
		except Exception as e:
			print("error in the risk agent")
			print(e)
			return {
				"error": str(e),
				"message": f"Error in risk analysis: {str(e)}",
				"status": "failed"
			}

		# 4. Security Validator (expects intent) - bypass agent framework
		try:
			print("running the security agent")
			# Normalize planner output
			if isinstance(planner_out, dict):
				intent_action = planner_out.get("action")
				intent_asset = planner_out.get("asset")
				intent_amount = planner_out.get("amount")
				intent_destination = planner_out.get("destination")
			else:
				intent_action = getattr(planner_out, "action", None)
				intent_asset = getattr(planner_out, "asset", None)
				intent_amount = getattr(planner_out, "amount", None)
				intent_destination = getattr(planner_out, "destination", None)

			from Agents.security_validator import _security_validate_impl
			security_out = _security_validate_impl(
				intent_action=intent_action,
				intent_asset=intent_asset,
				intent_amount=intent_amount,
				intent_destination=intent_destination,
			)
			print("security_out", security_out)
			if isinstance(security_out, dict) and not security_out.get("valid", True):
				# Add message to security rejection
				reasons = security_out.get("reasons", [])
				message = "Transaction rejected by security validation. " + "; ".join(reasons) if reasons else "Transaction rejected by security validation."
				security_out["message"] = message
				security_out["status"] = "rejected"
				return security_out
		except Exception as e:
			print(e)
			print("error in the security agent")
			return {
				"error": str(e),
				"message": f"Error in security validation: {str(e)}",
				"status": "failed"
			}

		# 5. Executor (uses intent) - bypass agent framework
		try:
			print("running the executor agent")
			# Normalize planner output
			if isinstance(planner_out, dict):
				intent_action = planner_out.get("action")
				intent_asset = planner_out.get("asset")
				intent_amount = planner_out.get("amount")
				intent_destination = planner_out.get("destination")
			else:
				intent_action = getattr(planner_out, "action", None)
				intent_asset = getattr(planner_out, "asset", None)
				intent_amount = getattr(planner_out, "amount", None)
				intent_destination = getattr(planner_out, "destination", None)

			from Agents.executor import _execute_transaction_impl
			exec_out = _execute_transaction_impl(
				intent_action=intent_action,
				intent_asset=intent_asset,
				intent_amount=intent_amount,
				intent_destination=intent_destination,
				user_id=user_id,
			)
			print("exec_out", exec_out)
			
			# If transaction requires confirmation (PIN), return executor output directly
			# Don't run auditor until transaction is actually completed
			if isinstance(exec_out, dict) and exec_out.get("requires_confirmation"):
				print("Transaction requires PIN confirmation, returning executor output")
				# Ensure message is present
				if "message" not in exec_out or not exec_out.get("message"):
					exec_out["message"] = "Transaction pending PIN confirmation. Please confirm to complete."
				return exec_out
			
			# Check if executor failed
			if isinstance(exec_out, dict):
				exec_status = exec_out.get("status")
				exec_error = exec_out.get("error")
				
				# If executor failed, return with message
				if exec_status == "failed" or exec_error:
					message = exec_error or "Transaction failed. Please check your wallet balance and try again."
					return {
						"transaction_id": None,
						"confirmed": False,
						"confirmation_hash": None,
						"status": "failed",
						"message": message,
						"echo_intent": exec_out.get("echo_intent", {})
					}
		except Exception as e:
			print(e)
			print("error in the executor agent")
			return {
				"transaction_id": None,
				"confirmed": False,
				"confirmation_hash": None,
				"status": "failed",
				"message": f"Error executing transaction: {str(e)}",
				"error": str(e)
			}

		# 6. Auditor - only runs if transaction doesn't require confirmation
		# (i.e., for mock/completed transactions)
		try:
			print("running the auditor agent")
			tx_id = None
			if isinstance(exec_out, dict):
				tx_id = exec_out.get("transaction_id")
			else:
				tx_id = getattr(exec_out, "transaction_id", None)

			from tools.agent_tools import _mock_audit_transaction_impl
			audit_out = _mock_audit_transaction_impl(tx_id)
			print("audit_out", audit_out)
			
			# Add message to audit output
			if isinstance(audit_out, dict):
				if audit_out.get("confirmed"):
					audit_out["message"] = "Transaction completed and confirmed successfully."
				else:
					audit_out["message"] = "Transaction is pending confirmation."
			else:
				# Convert to dict if needed
				audit_out = {
					"transaction_id": getattr(audit_out, "transaction_id", None),
					"confirmed": getattr(audit_out, "confirmed", False),
					"confirmation_hash": getattr(audit_out, "confirmation_hash", None),
					"message": "Transaction completed and confirmed successfully." if getattr(audit_out, "confirmed", False) else "Transaction is pending confirmation."
				}
		except Exception as e:
			print(e)
			print("error in the auditor agent")
			return {
				"transaction_id": None,
				"confirmed": False,
				"confirmation_hash": None,
				"status": "failed",
				"message": f"Error auditing transaction: {str(e)}",
				"error": str(e)
			}

		return audit_out