from fastapi import APIRouter
from order_api.services.order_service import OrderService

order_router = APIRouter()
order_service = OrderService()

@order_router.post("/")
def place_order(order_data: dict):
    order_id = order_service.place_order(order_data)
    return {"order_id": order_id}


@order_router.put("/{order_id}")
def modify_order(order_id: str, updated_price: float):
    success = order_service.modify_order(order_id, updated_price)
    return {"success": success}


@order_router.delete("/{order_id}")
def cancel_order(order_id: str):
    success = order_service.cancel_order(order_id)
    return {"success": success}

@order_router.get("/{order_id}")
def fetch_order(order_id: str):
    order = order_service.fetch_order(order_id)
    return order

@order_router.get("/")
def fetch_all_orders():
    return order_service.fetch_all_orders()
