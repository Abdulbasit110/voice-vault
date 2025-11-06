import uuid
import os
from agents import Agent, function_tool
from typing import Dict, Any, Optional

def _execute_transaction_impl(
    intent_action: Optional[str] = None,
    intent_asset: Optional[str] = None,
    intent_amount: Optional[float] = None,
    intent_destination: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute transaction by creating a Circle transfer challenge
    Returns challengeId for frontend PIN confirmation
    """
    try:
        from services.circle_wallet_service import get_circle_service
        
        # Get user_id from parameter or environment
        if not user_id:
            user_id = os.getenv("DEFAULT_USER_ID")
        
        if not user_id:
            return {
                "error": "user_id is required",
                "status": "failed",
                "echo_intent": {
                    "action": intent_action,
                    "asset": intent_asset,
                    "amount": intent_amount,
                    "destination": intent_destination,
                },
            }
        
        circle = get_circle_service()
        
        # Only handle transfer transactions for now
        if intent_action != "transfer" or not intent_destination:
            return {
                "challenge_id": None,
                "status": "skipped",
                "message": f"{intent_action} {intent_amount} {intent_asset} - Only transfers are supported",
                "requires_confirmation": False,
                "echo_intent": {
                    "action": intent_action,
                    "asset": intent_asset,
                    "amount": intent_amount,
                    "destination": intent_destination,
                },
            }
        
        # Get user's wallet
        wallets_response = circle.get_wallets(user_id)
        wallets = wallets_response.get("wallets", [])
        
        if not wallets:
            return {
                "error": "No wallet found for user",
                "status": "failed",
                "echo_intent": {
                    "action": intent_action,
                    "asset": intent_asset,
                    "amount": intent_amount,
                    "destination": intent_destination,
                },
            }
        
        wallet_id = wallets[0]["id"]
        
        # Get user session token
        session = circle.get_session_token(user_id)
        user_token = session["user_token"]
        encryption_key = session["encryption_key"]
        
        # Get wallet balance to find USDC token_id
        balance_data = circle.get_wallet_balance(
            wallet_id=wallet_id,
            user_token=user_token,
            include_all=True
        )
        
        token_balances = balance_data.get("tokenBalances", [])
        usdc_token_id = None
        
        for token_balance in token_balances:
            token_info = token_balance.get("token", {})
            if token_info.get("symbol") == "USDC":
                usdc_token_id = token_info.get("id")
                break
        
        if not usdc_token_id:
            return {
                "error": "USDC token not found in wallet",
                "status": "failed",
                "echo_intent": {
                    "action": intent_action,
                    "asset": intent_asset,
                    "amount": intent_amount,
                    "destination": intent_destination,
                },
            }
        
        # Convert amount to token units (USDC has 6 decimals)
        amount_token_units = str(int(intent_amount * 1_000_000))
        
        # Create transfer challenge
        challenge_response = circle.create_transfer_challenge(
            user_token=user_token,
            wallet_id=wallet_id,
            destination_address=intent_destination,
            amount=amount_token_units,
            token_id=usdc_token_id,
            fee_level="HIGH"
        )
        
        challenge_id = challenge_response.get("challengeId")
        
        # Get App ID for frontend
        app_id = circle.get_app_id()
        
        return {
            "challenge_id": challenge_id,
            "status": "pending_confirmation",
            "requires_confirmation": True,
            "user_id": user_id,
            "user_token": user_token,
            "encryption_key": encryption_key,
            "app_id": app_id,
            "wallet_id": wallet_id,
            "message": f"Transfer challenge created. Confirm with PIN to complete.",
            "echo_intent": {
                "action": intent_action,
                "asset": intent_asset,
                "amount": intent_amount,
                "destination": intent_destination,
            },
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "requires_confirmation": False,
            "echo_intent": {
                "action": intent_action,
                "asset": intent_asset,
                "amount": intent_amount,
                "destination": intent_destination,
            },
        }

@function_tool
def execute_transaction(
    intent_action: Optional[str] = None,
    intent_asset: Optional[str] = None,
    intent_amount: Optional[float] = None,
    intent_destination: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Execute transaction by creating Circle transfer challenge."""
    return _execute_transaction_impl(intent_action, intent_asset, intent_amount, intent_destination, user_id)


def build_executor_agent() -> Agent:
    instructions = (
        "You are the Executor. Use the provided tool to create a transfer challenge "
        "for user confirmation. Return challenge_id and status."
    )
    agent = Agent(
        name="ExecutorAgent",
        instructions=instructions,
        tools=[execute_transaction],
        model="gpt-4o-mini",
    )
    return agent
