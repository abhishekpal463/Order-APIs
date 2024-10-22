from fastapi import APIRouter

from order_api.services.trade_service import TradeService

trade_router = APIRouter()
trade_service = TradeService()

@trade_router.get("/")
def fetch_all_trades():
    return trade_service.fetch_all_trades()
