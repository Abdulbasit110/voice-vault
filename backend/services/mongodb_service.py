from pymongo import MongoClient
from typing import Optional
import os

class MongoDBService:
    def __init__(self):
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/voicevault")
        self.client = MongoClient(mongodb_uri)
        self.db = self.client.get_database("voicevault")
        self.transactions = self.db.transactions
        self.portfolios = self.db.portfolios
    
    def create_transaction(self, transaction_data: dict):
        """Insert a new transaction"""
        return self.transactions.insert_one(transaction_data)
    
    def get_transactions(self, user_id: str = "default_user"):
        """Get all transactions for a user"""
        return list(self.transactions.find({"user_id": user_id}))
    
    def update_portfolio(self, user_id: str, portfolio_data: dict):
        """Update user portfolio"""
        return self.portfolios.update_one(
            {"user_id": user_id},
            {"$set": portfolio_data},
            upsert=True
        )
    
    def get_portfolio(self, user_id: str = "default_user"):
        """Get user portfolio"""
        return self.portfolios.find_one({"user_id": user_id})

