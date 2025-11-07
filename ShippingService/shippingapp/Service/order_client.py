import requests
from django.conf import settings

USE_MOCK = getattr(settings, "USE_MOCK_ORDER", True)
ORDER_SERVICE_URL = getattr(settings, "ORDER_SERVICE_URL", "http://127.0.0.1:8001/v1/orders")


def get_order_details(order_id):
    """
    Get order details from Order Service.
    Returns dict or None if unavailable.
    In mock mode, returns an order structure that includes 'items' so inventory updates work.
    """
    if USE_MOCK:
        print(f"[MOCK] Fetching order details for order_id={order_id}")
        # Provide a realistic mock order including items (so shipping can update inventory)
        return {
            "order_id": order_id,
            "order_status": "CONFIRMED",
            "payment_status": "PAID",
            "items": [
                {"item_id": 1, "quantity": 2},
                {"item_id": 2, "quantity": 1}
            ]
        }

    try:
        resp = requests.get(f"{ORDER_SERVICE_URL}/{order_id}/detail/", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to reach Order Service: {e}")
    return None


def update_order_shipping_status(order_id, shipping_status):
    """
    Update the shipping status of an order in Order Service.
    PATCH /v1/orders/{id}/update/
    Returns True on success.
    """
    if USE_MOCK:
        print(f"[MOCK] Updating order {order_id} shipping_status={shipping_status}")
        return True

    try:
        resp = requests.patch(
            f"{ORDER_SERVICE_URL}/{order_id}/update/",
            json={"shipping_status": shipping_status},
            timeout=5,
        )
        if resp.status_code == 200:
            print(f"[INFO] Order {order_id} updated with shipping_status={shipping_status}")
            return True
        print(f"[WARN] Order update failed ({resp.status_code}): {resp.text}")
    except requests.RequestException as e:
        print(f"[ERROR] OrderService request failed: {e}")
    return False
