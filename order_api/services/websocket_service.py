import asyncio
from order_api.services.order_service import OrderService
from order_api.services.trade_service import TradeService


class WebSocketService:
    def __init__(self, order_service: OrderService, trade_service: TradeService):
        self.order_service = order_service
        self.trade_service = trade_service

    async def send_order_snapshot(self, websocket, depth=5):
        """Send the order book snapshot over the WebSocket connection."""
        try:
            while True:
                # Fetch the snapshot of the top N bids and asks
                bid_snapshot, ask_snapshot = self.order_service.get_order_snapshot(depth)

                # Send the snapshot as JSON over the WebSocket
                await websocket.send_json({
                    "bids": bid_snapshot,
                    "asks": ask_snapshot
                })

                # Wait for 1 second before sending the next snapshot
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error occurred while sending order snapshot: {e}")
            await websocket.close()

    async def notify_trades(self, websocket):
        """Send trade updates over the WebSocket connection as they occur."""
        try:
            last_trade_count = len(self.trade_service.fetch_all_trades())

            while True:
                # Fetch all trades
                all_trades = self.trade_service.fetch_all_trades()
                current_trade_count = len(all_trades)

                # If new trades have occurred, send them to the WebSocket
                if current_trade_count > last_trade_count:
                    new_trades = all_trades[last_trade_count:]
                    for trade in new_trades:
                        await websocket.send_json({
                            "trade_id": trade.trade_id,
                            "bid_order_id": trade.bid_order_id,
                            "ask_order_id": trade.ask_order_id,
                            "execution_timestamp": trade.execution_timestamp.isoformat(),
                            "price": trade.price,
                            "quantity": trade.quantity
                        })
                    last_trade_count = current_trade_count

                # Wait for 1 second before checking again
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error occurred while notifying trades: {e}")
            await websocket.close()
