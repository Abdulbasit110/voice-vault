from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Transaction(BaseModel):
    id: Optional[str] = None
    user_id: str
    type: str  # "buy", "sell", "transfer"
    asset: str  # "ETH", "BTC", "USDC"
    amount: float
    value: float  # USD value
    date: str
    status: str  # "pending", "completed", "failed"
    transaction_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    
class TransactionCreate(BaseModel):
    user_id: str
    type: str
    asset: str
    amount: float
    value: float
    transaction_hash: Optional[str] = None

