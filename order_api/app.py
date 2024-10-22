from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from order_api.services.order_service import OrderService
from order_api.services.trade_service import TradeService
from order_api.services.websocket_service import WebSocketService
from order_api.api.orders import order_router
from order_api.api.trades import trade_router
from order_api.api.websockets import websocket_router
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Initialize services
order_service = OrderService()
trade_service = TradeService()
websocket_service = WebSocketService(order_service, trade_service)

# Routers
app.include_router(websocket_router)
app.include_router(order_router, prefix="/orders")
app.include_router(trade_router, prefix="/trades")


# @app.websocket("/ws/snapshot")
# async def snapshot_endpoint(websocket: WebSocket):
#     await websocket_service.send_order_snapshot(websocket)
#
# @app.websocket("/ws/trades")
# async def trades_endpoint(websocket: WebSocket):
#     await websocket_service.notify_trades(websocket)
