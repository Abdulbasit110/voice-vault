from pymongo import MongoClient
from typing import Optional
import os
from datetime import datetime
import base64

class MongoDBService:
    _instance = None
    _client = None
    
    def __new__(cls):
        """Singleton pattern to ensure one MongoDB connection"""
        if cls._instance is None:
            cls._instance = super(MongoDBService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if MongoDBService._client is None:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/voicevault")
            MongoDBService._client = MongoClient(mongodb_uri)
            self.db = MongoDBService._client.get_database("voicevault")
            self.transactions = self.db.transactions
            self.portfolios = self.db.portfolios
            self.audio_files = self.db.audio_files
            self.circle_users = self.db.circle_users
            self.contacts = self.db.contacts
        else:
            # Reuse existing connection
            self.db = MongoDBService._client.get_database("voicevault")
            self.transactions = self.db.transactions
            self.portfolios = self.db.portfolios
            self.audio_files = self.db.audio_files
            self.circle_users = self.db.circle_users
            self.contacts = self.db.contacts
    
    @property
    def client(self):
        """Return the MongoDB client"""
        return MongoDBService._client
    
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
    
    def save_audio(self, audio_data: bytes, user_id: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        """
        Save audio file to MongoDB GridFS or as binary data
        
        Args:
            audio_data: Audio file bytes
            user_id: Optional user ID
            metadata: Optional metadata dict (e.g., {"source": "stt", "format": "webm"})
        
        Returns:
            Document ID of saved audio
        """
        from bson import Binary
        
        audio_doc = {
            "audio_data": Binary(audio_data),
            "size": len(audio_data),
            "user_id": user_id or "default_user",
            "created_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        result = self.audio_files.insert_one(audio_doc)
        return str(result.inserted_id)
    
    def save_audio_base64(self, base64_audio: str, user_id: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        """
        Save base64 encoded audio to MongoDB
        
        Args:
            base64_audio: Base64 encoded audio string
            user_id: Optional user ID
            metadata: Optional metadata dict
        
        Returns:
            Document ID of saved audio
        """
        # Decode base64 to bytes
        audio_bytes = base64.b64decode(base64_audio)
        return self.save_audio(audio_bytes, user_id, metadata)
    
    def get_audio(self, audio_id: str) -> Optional[bytes]:
        """
        Retrieve audio file from MongoDB by ID
        
        Args:
            audio_id: MongoDB document ID
        
        Returns:
            Audio bytes or None if not found
        """
        from bson import ObjectId
        
        try:
            audio_doc = self.audio_files.find_one({"_id": ObjectId(audio_id)})
            if audio_doc and "audio_data" in audio_doc:
                return audio_doc["audio_data"]
        except Exception as e:
            print(f"Error retrieving audio: {e}")
        return None
    
    def get_user_audio_files(self, user_id: str, limit: int = 10):
        """
        Get recent audio files for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of files to return
        
        Returns:
            List of audio file documents (without binary data)
        """
        return list(
            self.audio_files.find(
                {"user_id": user_id},
                {"audio_data": 0}  # Exclude binary data for listing
            )
            .sort("created_at", -1)
            .limit(limit)
        )
    
    def save_circle_user_initial(self, user_id: str, metadata: Optional[dict] = None) -> str:
        """
        Save Circle user when first created (before wallet is created)
        
        Args:
            user_id: Circle user ID
            metadata: Optional additional metadata
        
        Returns:
            Document ID of saved user
        """
        user_doc = {
            "user_id": user_id,
            "wallet_address": None,  # Will be updated when wallet is created
            "wallet_id": None,
            "blockchain": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        # Upsert: update if exists, insert if not
        result = self.circle_users.update_one(
            {"user_id": user_id},
            {"$set": {**user_doc, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        
        # Get the document ID
        if result.upserted_id:
            return str(result.upserted_id)
        else:
            # Document already existed, find and return its ID
            existing = self.circle_users.find_one({"user_id": user_id})
            return str(existing["_id"]) if existing else ""
    
    def save_circle_user(self, user_id: str, wallet_address: str, wallet_id: Optional[str] = None, blockchain: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        """
        Save Circle wallet user to MongoDB
        
        Args:
            user_id: Circle user ID
            wallet_address: Wallet address
            wallet_id: Optional Circle wallet ID
            blockchain: Optional blockchain network (e.g., "ETH-SEPOLIA")
            metadata: Optional additional metadata
        
        Returns:
            Document ID of saved user
        """
        user_doc = {
            "user_id": user_id,
            "wallet_address": wallet_address,
            "wallet_id": wallet_id,
            "blockchain": blockchain,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        # Upsert: update if exists, insert if not
        result = self.circle_users.update_one(
            {"user_id": user_id},
            {"$set": {**user_doc, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        
        # Get the document ID
        if result.upserted_id:
            return str(result.upserted_id)
        else:
            # Document already existed, find and return its ID
            existing = self.circle_users.find_one({"user_id": user_id})
            return str(existing["_id"]) if existing else ""
    
    def get_circle_user(self, user_id: str) -> Optional[dict]:
        """
        Get Circle wallet user by user_id
        
        Args:
            user_id: Circle user ID
        
        Returns:
            User document or None if not found
        """
        return self.circle_users.find_one({"user_id": user_id})
    
    def get_circle_user_by_address(self, wallet_address: str) -> Optional[dict]:
        """
        Get Circle wallet user by wallet address
        
        Args:
            wallet_address: Wallet address
        
        Returns:
            User document or None if not found
        """
        return self.circle_users.find_one({"wallet_address": wallet_address})
    
    def update_circle_user(self, user_id: str, update_data: dict) -> bool:
        """
        Update Circle wallet user data
        
        Args:
            user_id: Circle user ID
            update_data: Dictionary of fields to update
        
        Returns:
            True if updated, False if not found
        """
        update_data["updated_at"] = datetime.utcnow()
        result = self.circle_users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def add_contact(self, user_id: str, wallet_address: str, name: str) -> str:
        """
        Add a contact for a user
        
        Args:
            user_id: Current user ID
            wallet_address: Contact's wallet address
            name: Contact name
        
        Returns:
            Document ID of saved contact
        """
        contact_doc = {
            "user_id": user_id,
            "wallet_address": wallet_address,
            "name": name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.contacts.insert_one(contact_doc)
        return str(result.inserted_id)
    
    def get_contacts(self, user_id: str) -> list:
        """
        Get all contacts for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of contact documents
        """
        return list(
            self.contacts.find({"user_id": user_id})
            .sort("name", 1)  # Sort alphabetically by name
        )
    
    def search_contacts_by_name(self, user_id: str, name: str) -> list:
        """
        Search contacts by name (case-insensitive partial match)
        
        Args:
            user_id: User ID
            name: Name to search for
        
        Returns:
            List of matching contact documents
        """
        import re
        # Case-insensitive regex search
        pattern = re.compile(name, re.IGNORECASE)
        return list(
            self.contacts.find({
                "user_id": user_id,
                "name": pattern
            })
            .sort("name", 1)
        )
    
    def delete_contact(self, contact_id: str, user_id: str) -> bool:
        """
        Delete a contact
        
        Args:
            contact_id: Contact document ID
            user_id: User ID (for security)
        
        Returns:
            True if deleted, False if not found
        """
        from bson import ObjectId
        
        try:
            result = self.contacts.delete_one({
                "_id": ObjectId(contact_id),
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting contact: {e}")
            return False

