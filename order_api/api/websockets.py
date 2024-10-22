from fastapi import APIRouter, WebSocket
from order_api.services.websocket_service import WebSocketService
from order_api.services.order_service import OrderService
from order_api.services.trade_service import TradeService

websocket_router = APIRouter()

# Instantiate the services
order_service = OrderService()
trade_service = TradeService()
websocket_service = WebSocketService(order_service, trade_service)

@websocket_router.websocket("/ws/snapshot")
async def order_book_snapshot(websocket: WebSocket):
    """WebSocket endpoint for sending order book snapshots."""
    await websocket.accept()
    await websocket_service.send_order_snapshot(websocket)

@websocket_router.websocket("/ws/trades")
async def trade_updates(websocket: WebSocket):
    """WebSocket endpoint for sending trade updates."""
    await websocket.accept()
    await websocket_service.notify_trades(websocket)
