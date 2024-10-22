from order_api.models import Order
from order_api.services.order_book import OrderBook
import uuid

class OrderService:
    def __init__(self):
        self.order_book = OrderBook()

    def place_order(self, order_data):
        order_data['order_id'] = str(uuid.uuid4())
        order = Order(**order_data)
        self.order_book.place_order(order)
        return order.order_id

    def modify_order(self, order_id, updated_price):
        return self.order_book.modify_order(order_id, updated_price)

    def cancel_order(self, order_id):
        return self.order_book.cancel_order(order_id)

    def fetch_order(self, order_id):
        return self.order_book.orders.get(order_id)

    def fetch_all_orders(self):
        return list(self.order_book.orders.values())


    def get_order_snapshot(self, depth=5):
        """Get a snapshot of the top bid and ask levels."""
        return self.order_book.get_order_snapshot(depth)
