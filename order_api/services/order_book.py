import redis
import pickle
import heapq
import uuid
from datetime import datetime
from order_api.models import Order, Trade


class OrderBook:
    def __init__(self):
        # Set up Redis connection
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        # Initialize in-memory data structures
        self.bids = []  # Max-heap for buy orders (bids)
        self.asks = []  # Min-heap for sell orders (asks)
        self.orders = {}  # Store orders by order_id
        self.trades = []  # Store trades

        # Load persisted state from Redis
        self.load_state()

    def load_state(self):
        """Load the persisted order book and orders from Redis."""
        bids = self.redis_client.get("order_book_bids")
        asks = self.redis_client.get("order_book_asks")
        orders = self.redis_client.get("orders")
        trades = self.redis_client.get("trades")

        # Deserialize using pickle if the data exists in Redis
        if bids:
            self.bids = pickle.loads(bids)
        if asks:
            self.asks = pickle.loads(asks)
        if orders:
            self.orders = pickle.loads(orders)
        if trades:
            self.trades = pickle.loads(trades)

    def save_state(self):
        """Persist the current state of the order book to Redis."""
        self.redis_client.set("order_book_bids", pickle.dumps(self.bids))
        self.redis_client.set("order_book_asks", pickle.dumps(self.asks))
        self.redis_client.set("orders", pickle.dumps(self.orders))
        self.redis_client.set("trades", pickle.dumps(self.trades))

    def place_order(self, order: Order):
        """Place an order in the order book and try to match it."""
        # Check if the order is a buy or sell
        if order.side == 1:  # Buy side (bid)
            # Match with the best available ask (lowest price)
            while self.asks and self.asks[0][0] <= order.price and order.quantity > 0:
                best_ask_price, best_ask_order = heapq.heappop(self.asks)
                self.execute_trade(order, best_ask_order)
            # If the order is not fully filled, add it to the bids
            if order.quantity > 0:
                heapq.heappush(self.bids, (-order.price, order))
        else:  # Sell side (ask)
            # Match with the best available bid (highest price)
            while self.bids and -self.bids[0][0] >= order.price and order.quantity > 0:
                best_bid_price, best_bid_order = heapq.heappop(self.bids)
                self.execute_trade(best_bid_order, order)
            # If the order is not fully filled, add it to the asks
            if order.quantity > 0:
                heapq.heappush(self.asks, (order.price, order))

        # Save the order in the order book
        self.orders[order.order_id] = order

        # Persist the state to Redis after placing the order
        self.save_state()

    def execute_trade(self, bid_order: Order, ask_order: Order):
        """Execute a trade between a buy and a sell order."""
        # Calculate the trade quantity and price
        traded_quantity = min(bid_order.quantity, ask_order.quantity)
        traded_price = ask_order.price  # The ask price is the trade price

        # Update the remaining quantity of the orders
        bid_order.quantity -= traded_quantity
        ask_order.quantity -= traded_quantity

        # Log the trade
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            bid_order_id=bid_order.order_id,
            ask_order_id=ask_order.order_id,
            execution_timestamp=datetime.now(),
            price=traded_price,
            quantity=traded_quantity
        )
        self.trades.append(trade)

        # Persist the state of the trades
        self.save_state()

        # Remove the orders if they are fully filled
        if bid_order.quantity == 0 and bid_order.order_id in self.orders:
            del self.orders[bid_order.order_id]

        if ask_order.quantity == 0 and ask_order.order_id in self.orders:
            del self.orders[ask_order.order_id]


    def cancel_order(self, order_id: str):
        """Cancel an order if it is still in the order book."""
        order = self.orders.pop(order_id, None)
        if order:
            # Remove the order from the corresponding heap
            if order.side == 1:
                self.bids = [(p, o) for p, o in self.bids if o.order_id != order_id]
                heapq.heapify(self.bids)
            else:
                self.asks = [(p, o) for p, o in self.asks if o.order_id != order_id]
                heapq.heapify(self.asks)

            # Persist the updated state
            self.save_state()
            return True
        return False

    def get_order_snapshot(self, depth=5):
        """Return a snapshot of the top N bid and ask levels."""
        bid_snapshot = [(abs(p), o.quantity) for p, o in self.bids[:depth]]
        ask_snapshot = [(p, o.quantity) for p, o in self.asks[:depth]]
        return bid_snapshot, ask_snapshot

    def fetch_all_trades(self):
        """Return all the trades that have occurred."""
        return self.trades

    def fetch_order(self, order_id: str):
        """Fetch details of a specific order by its order_id."""
        return self.orders.get(order_id, None)
