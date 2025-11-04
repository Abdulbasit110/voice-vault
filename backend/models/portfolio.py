from pydantic import BaseModel
from typing import List, Optional

class Asset(BaseModel):
    name: str
    value: float
    amount: float
    percentage: float

class Portfolio(BaseModel):
    user_id: str
    total_value: float
    assets: List[Asset]
    allocations: dict
    
class PortfolioResponse(BaseModel):
    total_value: float
    assets: List[Asset]
    allocations: dict

