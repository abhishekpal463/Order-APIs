from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Order(BaseModel):
    order_id: Optional[str]
    side: int  # 1 for buy, -1 for sell
    quantity: int
    price: float
    traded_quantity: int = 0
    average_traded_price: Optional[float] = 0.0
    alive: bool = True

class Trade(BaseModel):
    trade_id: str
    bid_order_id: str
    ask_order_id: str
    execution_timestamp: datetime
    price: float
    quantity: int
