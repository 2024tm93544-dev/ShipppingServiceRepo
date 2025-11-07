import requests
from django.conf import settings

USE_MOCK = getattr(settings, "USE_MOCK_INVENTORY", True)
# keep default consistent with settings.py
INVENTORY_SERVICE_URL = getattr(
    settings,
    "INVENTORY_SERVICE_URL",
    "http://127.0.0.1:8002/v1/inventory"
)

# Mock inventory data (in-memory)
_MOCK_INVENTORY = {}


def get_inventory_for_items(item_ids):
    """
    Fetch inventory for given item IDs.
    Uses mock data if USE_MOCK=True.
    Returns a list of inventory dicts in the same order as item_ids.
    """
    if USE_MOCK:
        print("[MOCK] Fetching inventory for:", item_ids)
        return _mock_inventory(item_ids)

    results = []
    for item_id in item_ids:
        try:
            resp = requests.get(f"{INVENTORY_SERVICE_URL}/{item_id}/", timeout=5)
            if resp.status_code == 200:
                results.append(resp.json())
            else:
                results.append({"item_id": item_id, "available_qty": 0})
        except requests.RequestException as e:
            print(f"[ERROR] InventoryService unavailable: {e}")
            results.append({"item_id": item_id, "available_qty": 0})
    return results


def _mock_inventory(item_ids):
    """Create and return fake inventory data for given item IDs (preserve order)."""
    # Ensure we create an entry for each requested id and return only requested items
    ordered = []
    for item_id in item_ids:
        # normalize key type for dictionary (use int if numeric)
        key = item_id
        if key not in _MOCK_INVENTORY:
            _MOCK_INVENTORY[key] = {"item_id": key, "available_qty": 50}
        ordered.append(_MOCK_INVENTORY[key])
    return ordered


def update_inventory(item_id, quantity_change):
    """
    Update inventory (deduct or add) for given item.
    Works in mock or live mode.

    quantity_change:
      - positive number = reduce stock by that amount
      - negative number = increase stock by that amount
    """
    if USE_MOCK:
        print(f"[MOCK] Updating inventory for item {item_id} by {quantity_change}")
        record = _MOCK_INVENTORY.get(item_id, {"item_id": item_id, "available_qty": 50})
        # Subtract positive quantity_change (reduce stock), add if negative
        record["available_qty"] = max(0, record.get("available_qty", 50) - quantity_change)
        _MOCK_INVENTORY[item_id] = record
        return record

    try:
        resp = requests.patch(
            f"{INVENTORY_SERVICE_URL}/{item_id}/update/",
            json={"quantity_change": quantity_change},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to update inventory: {e}")
    return {"item_id": item_id, "available_qty": 0}
