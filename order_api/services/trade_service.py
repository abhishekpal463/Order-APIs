import redis
import pickle
import uuid
from order_api.models import Trade
from datetime import datetime



class TradeService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.trades = []

        # Load persisted trade state on startup
        self.load_state()


    def log_trade(self, bid_order_id: str, ask_order_id: str, price: float, quantity: int):
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            bid_order_id=bid_order_id,
            ask_order_id=ask_order_id,
            execution_timestamp=datetime.now(),
            price=price,
            quantity=quantity
        )
        self.trades.append(trade)

        # Persist the new trade after logging
        self.save_state()

    def fetch_all_trades(self):
        return self.trades

    def save_state(self):
        # Persist the trades to Redis
        self.redis_client.set("trades", pickle.dumps(self.trades))

    def load_state(self):
        # Load the persisted trades from Redis
        trades = self.redis_client.get("trades")

        if trades:
            self.trades = pickle.loads(trades)
