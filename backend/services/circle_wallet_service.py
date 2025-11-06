import os
import uuid
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class CircleWalletService:
    """
    Circle User Controlled Wallets REST API wrapper
    Based on: https://developers.circle.com/interactive-quickstarts/user-controlled-wallets
    """
    
    def __init__(self):
        self.api_key = os.getenv("CIRCLE_API_KEY")
        if not self.api_key:
            raise ValueError("CIRCLE_API_KEY must be set in .env")
        
        self.base_url = "https://api.circle.com/v1/w3s"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def get_app_id(self) -> str:
        """
        Get App ID from Circle config
        Returns: App ID string
        """
        url = f"{self.base_url}/config/entity"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        print("response",response.json())
        return response.json()["data"]["appId"]
    
    def create_user(self, user_id: str) -> Dict[str, Any]:
        """
        Step 1: Create a new user
        """
        url = f"{self.base_url}/users"
        payload = {"userId": user_id}
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()["data"]
    
    def get_session_token(self, user_id: str) -> Dict[str, Any]:
        """
        Step 2: Get user session token (60-min validity)
        Returns: {userToken, encryptionKey}
        """
        url = f"{self.base_url}/users/token"
        payload = {"userId": user_id}
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()["data"]
        return {
            "user_token": data["userToken"],
            "encryption_key": data["encryptionKey"]
        }
    
    def initialize_user(self, user_token: str, blockchains: list = None) -> Dict[str, Any]:
        """
        Step 3: Initialize user and create wallet
        Returns: {challengeId} - for PIN setup via WebSDK
        """
        if blockchains is None:
            blockchains = ["ETH-SEPOLIA"]  # Testnet
        
        url = f"{self.base_url}/user/initialize"
        payload = {
            "idempotencyKey": str(uuid.uuid4()),
            "blockchains": blockchains,
            "accountType": "SCA"  # Smart Contract Account
        }
        
        headers = {**self.headers, "X-User-Token": user_token}
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()["data"]
    
    def get_wallets(self, user_id: str) -> Dict[str, Any]:
        """
        Get all wallets for a user
        """
        url = f"{self.base_url}/wallets?userId={user_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()["data"]
    
    def get_wallet_balance(self, wallet_id: str, user_token: str, include_all: bool = True) -> Dict[str, Any]:
        """
        Get token balance for a wallet
        Requires user_token for authentication
        
        Args:
            wallet_id: Wallet ID
            user_token: User session token
            include_all: Return all resources with monitored and non-monitored tokens (default: True)
        
        Returns:
            Wallet balance data with tokenBalances array
        """
        url = f"{self.base_url}/wallets/{wallet_id}/balances"
        
        params = {
            "includeAll": include_all
        }
        
        headers = {**self.headers, "X-User-Token": user_token}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()["data"]
    
    def list_transactions(self, user_id: str, user_token: str, page_size: int = 50, page_before: Optional[str] = None, page_after: Optional[str] = None) -> Dict[str, Any]:
        """
        List transactions for a user
        Requires user_token for authentication
        
        Args:
            user_id: User ID
            user_token: User session token
            page_size: Number of transactions per page (default: 50)
            page_before: Cursor for pagination (before)
            page_after: Cursor for pagination (after)
        
        Returns:
            List of transactions
        """
        # First, get the user's wallet
        wallets_response = self.get_wallets(user_id)
        wallets = wallets_response.get("wallets", [])
        
        if not wallets:
            # Return empty list if no wallet exists
            return {"transactions": [], "pageBefore": None, "pageAfter": None}
        
        # Use the first wallet to get transactions
        wallet_id = wallets[0]["id"]
        
        # List transactions for the wallet
        url = f"{self.base_url}/transactions"
        
        params = {
            "walletId": wallet_id,
            "pageSize": page_size
        }
        
        if page_before:
            params["pageBefore"] = page_before
        if page_after:
            params["pageAfter"] = page_after
        
        headers = {**self.headers, "X-User-Token": user_token}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()["data"]
    
    def get_transaction(self, transaction_id: str, user_token: str) -> Dict[str, Any]:
        """
        Get a single transaction by ID
        Requires user_token for authentication
        
        Args:
            transaction_id: Transaction ID
            user_token: User session token
        
        Returns:
            Transaction details
        """
        url = f"{self.base_url}/transactions/{transaction_id}"
        
        headers = {**self.headers, "X-User-Token": user_token}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()["data"]
    
    def create_transfer_challenge(
        self,
        user_token: str,
        wallet_id: str,
        destination_address: str,
        amount: str,
        token_id: str,
        fee_level: str = "HIGH"
    ) -> Dict[str, Any]:
        """
        Create a transfer challenge for user confirmation
        Requires user_token for authentication
        
        Args:
            user_token: User session token
            wallet_id: Source wallet ID
            destination_address: Recipient address
            amount: Amount in token units (string, e.g., "1000000" for 1 USDC with 6 decimals)
            token_id: Token ID to transfer
            fee_level: Fee level (LOW, MEDIUM, HIGH) - default HIGH
        
        Returns:
            Challenge data with challengeId
        """
        url = f"{self.base_url}/user/transactions/transfer"
        
        payload = {
            "idempotencyKey": str(uuid.uuid4()),
            "walletId": wallet_id,
            "destinationAddress": destination_address,
            "amounts": [amount],  # Amount in decimal format (e.g., "0.1" for 0.1 USDC)
            "tokenId": token_id,
            "feeLevel": fee_level
        }
        
        headers = {**self.headers, "X-User-Token": user_token}
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()["data"]
    
    def create_transfer_challenge_with_address(
        self,
        user_token: str,
        wallet_id: str,
        destination_address: str,
        amount: str,
        token_address: str,
        blockchain: str,
        fee_level: str = "HIGH"
    ) -> Dict[str, Any]:
        """
        Create a transfer challenge using tokenAddress + blockchain (alternative to tokenId)
        Requires user_token for authentication
        
        Args:
            user_token: User session token
            wallet_id: Source wallet ID
            destination_address: Recipient address
            amount: Amount in token units (string, e.g., "1000000" for 1 USDC with 6 decimals)
            token_address: Token contract address (e.g., USDC address)
            blockchain: Blockchain network (e.g., "ETH-SEPOLIA")
            fee_level: Fee level (LOW, MEDIUM, HIGH) - default HIGH
        
        Returns:
            Challenge data with challengeId
        """
        url = f"{self.base_url}/user/transactions/transfer"
        
        payload = {
            "idempotencyKey": str(uuid.uuid4()),
            "walletId": wallet_id,
            "destinationAddress": destination_address,
            "amounts": [amount],  # Amount in decimal format (e.g., "0.1" for 0.1 USDC)
            "tokenAddress": token_address,
            "blockchain": blockchain,
            "feeLevel": fee_level
        }
        
        headers = {**self.headers, "X-User-Token": user_token}
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()["data"]


# Singleton
_circle_service: Optional[CircleWalletService] = None

def get_circle_service() -> CircleWalletService:
    """Get or create Circle service singleton"""
    global _circle_service
    if _circle_service is None:
        _circle_service = CircleWalletService()
    return _circle_service

