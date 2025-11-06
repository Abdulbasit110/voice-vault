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
        
        # Normalize "send" to "transfer"
        normalized_action = intent_action
        if intent_action == "send":
            normalized_action = "transfer"
        
        # Only handle transfer transactions for now
        if normalized_action != "transfer" or not intent_destination:
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
        wallet_blockchain = wallets[0].get("blockchain", "ETH-SEPOLIA")  # Default to testnet
        
        # Get user session token
        session = circle.get_session_token(user_id)
        user_token = session["user_token"]
        encryption_key = session["encryption_key"]
        
        # Get wallet balance to find USDC token_id and verify balance
        usdc_token_id = None
        usdc_balance = 0.0
        try:
            balance_data = circle.get_wallet_balance(
                wallet_id=wallet_id,
                user_token=user_token,
                include_all=True
            )
            
            token_balances = balance_data.get("tokenBalances", [])
            print(f"Found {len(token_balances)} token balances")
            
            for token_balance in token_balances:
                token_info = token_balance.get("token", {})
                symbol = token_info.get("symbol", "").upper()
                print(f"Token: {symbol}, Amount: {token_balance.get('amount')}")
                
                if symbol == "USDC":
                    usdc_token_id = token_info.get("id")
                    # Calculate balance in human-readable format
                    decimals = token_info.get("decimals", 6)
                    amount_raw = token_balance.get("amount", "0")
                    usdc_balance = float(amount_raw) / (10 ** decimals)
                    print(f"USDC Token ID: {usdc_token_id}, Balance: {usdc_balance} USDC")
                    break
        except Exception as balance_error:
            print(f"Warning: Could not get wallet balance: {balance_error}")
            print("Will use tokenAddress + blockchain instead")
        
        # Balance check disabled - let Circle API validate balance
        # Note: Wallet currently has {usdc_balance:.6f} USDC, attempting to send {intent_amount} USDC
        if usdc_balance > 0:
            print(f"Warning: Wallet balance is {usdc_balance:.6f} USDC, attempting to send {intent_amount} USDC")
        
        # Convert amount to token units (USDC has 6 decimals)
        # Format as decimal string per Circle API requirements
        amount_token_units = f"{intent_amount:.6f}"  # e.g., "0.100000"
        
        # USDC token addresses for different networks
        # For ETH-SEPOLIA testnet: Use Circle's monitored USDC
        # For mainnet: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
        usdc_token_addresses = {
            "ETH-SEPOLIA": "",  # Empty for native/monitored tokens - use tokenId instead
            "ETH": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        }
        
        # Create transfer challenge
        # Prefer tokenId if available (more reliable)
        if usdc_token_id:
            print(f"Creating transfer challenge with tokenId: {usdc_token_id}, amount: {amount_token_units}")
            challenge_response = circle.create_transfer_challenge(
                user_token=user_token,
                wallet_id=wallet_id,
                destination_address=intent_destination,
                amount=amount_token_units,
                token_id=usdc_token_id,
                fee_level="MEDIUM"  # Changed to MEDIUM to reduce fees
            )
        else:
            # Use tokenAddress + blockchain as fallback
            usdc_address = usdc_token_addresses.get(wallet_blockchain)
            if not usdc_address and wallet_blockchain == "ETH-SEPOLIA":
                # For testnet, try to use empty address (native token) or get tokenId from Circle
                return {
                    "error": "USDC token not found in wallet. Please ensure you have USDC balance. Use tokenId instead of tokenAddress.",
                    "status": "failed",
                    "requires_confirmation": False,
                    "echo_intent": {
                        "action": intent_action,
                        "asset": intent_asset,
                        "amount": intent_amount,
                        "destination": intent_destination,
                    },
                }
            
            print(f"Creating transfer challenge with tokenAddress: {usdc_address}, amount: {amount_token_units}")
            challenge_response = circle.create_transfer_challenge_with_address(
                user_token=user_token,
                wallet_id=wallet_id,
                destination_address=intent_destination,
                amount=amount_token_units,
                token_address=usdc_address,
                blockchain=wallet_blockchain,
                fee_level="MEDIUM"  # Changed to MEDIUM to reduce fees
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
